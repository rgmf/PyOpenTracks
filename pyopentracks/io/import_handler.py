"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>.

This file is part of PyOpenTracks.

PyOpenTracks is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

PyOpenTracks is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOpenTracks. If not, see <https://www.gnu.org/licenses/>.
"""

import threading

from os import path
from pathlib import Path
from typing import List
from xml.etree.ElementTree import XMLParser

from gi.repository import GLib, GObject

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.io.gpx_parser import GpxParser
from pyopentracks.io.fit_parser import FitParser
from pyopentracks.io.result import Result
from pyopentracks.io.result import RecordedWith
from pyopentracks.models.database import Database
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.auto_import import AutoImport
from pyopentracks.tasks.gain_loss_filter import GainLossFilter


class ImportHandler:
    def __init__(self):
        self._callback = None
        self._opentracks_gain_loss_correction = False

    def with_opentracks_gain_loss_correction(self):
        """Add OpenTracks gain and loss correction when importing.

        If the track was recorded with OpenTracks then it'll try to correct
        gain and loss if a barometric sensor was used and added to file to be
        imported.
        """
        self._opentracks_gain_loss_correction = True
        return self

    def _import_finished(self, result):
        raise NotImplementedError

    def _import_track(self, import_result):
        """Import track if not exists.

        This method is called when parsing is finished and it checks
        if track exists for importing it or not.

        Arguments:
        import_result -- Result object.
        """
        if not import_result.is_ok or not import_result.track:
            result = Result(
                code=Result.ERROR,
                filename=import_result.filename,
                message=import_result.message,
                recorded_with=import_result.recorded_with
            )
        else:
            track = import_result.track
            try:
                db = Database()
                tracks = db.get_existed_tracks(
                    track.uuid, track.start_time_ms, track.end_time_ms
                )
                if tracks:
                    # Track exists
                    result = Result(
                        code=Result.EXISTS,
                        track=track,
                        filename=import_result.filename,
                        message=_("Track already exists"),
                        recorded_with=import_result.recorded_with
                    )
                else:
                    # Track doesn't exists -> make importing.
                    result = self._import(
                        track,
                        import_result.filename,
                        import_result.recorded_with
                    )

            except Exception as error:
                pyot_logging.get_logger(__name__).exception(str(error))
                result = Result(
                    code=Result.ERROR,
                    filename=import_result.filename,
                    message=str(error),
                    recorded_with=import_result.recorded_with
                )

        self._import_finished(result)

    def _import(self, track, filename, recorded_with):
        """Makes the importing of the track.

        It inserts the track and its track points to the database.

        This method assumes track can be inserted in the database.

        Arguments:
        track         -- Track object to be inserted in the database.
        filename      -- original filename.
        recorded_with -- source of track recording.

        Return:
        Result object.
        """
        trackid = DatabaseHelper.insert(track)
        if not trackid:
            code = Result.ERROR
            message = _(
                f"Error importing the file {filename}."
                "\nIt couldn't be inserted in the database"
            )
        else:
            DatabaseHelper.bulk_insert(track.track_points, trackid)
            code = Result.OK
            message = _("Track imported")

        if code == Result.OK and recorded_with.is_opentracks() and self._opentracks_gain_loss_correction:
            res_gain_loss_filter = GainLossFilter(trackid).run()
            if res_gain_loss_filter is None:
                message = f"Error filtering gain and loss for the file {filename}"
                pyot_logging.get_logger(__name__).error(message)

        return Result(
            code=code,
            track=track,
            filename=filename,
            message=message,
            recorded_with=recorded_with
        )


class ImportFileHandler(ImportHandler):

    def __init__(self, path, cb):
        """
        Arguments:
        path     -- the filename to be parsed.
        callback -- a function that accept Track object to be
                    called when parsing and importing is finished.
                    It's a function used to get the result of the
                    parsing and importing process.
        """
        super().__init__()
        self._filename = path
        self._callback = cb

    def run(self):
        thread = threading.Thread(target=self._import_in_thread)
        thread.daemon = True
        thread.start()

    def _import_in_thread(self):
        parser = ParserHandler()
        result = parser.parse(self._filename)
        self._import_track(result)

    def _import_finished(self, result):
        GLib.idle_add(self._callback, result)


class ImportFolderHandler(ImportHandler, GObject.GObject):

    __gsignals__ = {
        "total-files-to-import": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)
        self._files_path: List[Path] = []
        self._callback = None
        self._thread = None
        self._result = {
            "folder": "",
            "total": 0,
            "imported": 0,
            "errors": []
        }

    def stop(self):
        if self._thread:
            self._thread.do_run = False

    def import_folder(self, folder_path: str, cb):
        self._result["folder"] = folder_path
        path_object = Path(self._result["folder"])

        # Select all GPX and FIT files from path folder.
        self._files_path = [f for f in path_object.glob("*.gpx")]
        self._files_path.extend([f for f in path_object.glob("*.fit")])

        self._result["total"] = len(self._files_path)
        self.emit("total-files-to-import", int(self._result["total"]))
        self._callback = cb

        self._thread = threading.Thread(target=self._import_in_thread, daemon=True)
        self._thread.start()

    def _import_in_thread(self):
        parser = ParserHandler()
        for f in self._files_path:
            result = parser.parse(str(f))
            self._import_track(result)
            if not getattr(self._thread, "do_run", True):
                break

    def _import_finished(self, result: Result):
        if result.is_ok:
            self._result["imported"] = self._result["imported"] + 1
        else:
            self._result["errors"].append(
                _(f"Error importing the file {result.filename}: {result.message}")
            )
        GLib.idle_add(self._callback, self._result)


class AutoImportHandler(ImportHandler, GObject.GObject):

    __gsignals__ = {
        "total-files-to-autoimport": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)
        self._folder = None
        self._callback = None
        self._imported = 0
        self._not_imported = 0
        self._total_to_import = 0

    def import_folder(self, path: str, cb):
        self._folder = path
        self._callback = cb
        thread = threading.Thread(target=self._checking_in_thread)
        thread.daemon = True
        thread.start()

    def _checking_in_thread(self):
        p = Path(self._folder)
        if not p.is_dir():
            return

        files_to_import = []
        parser = ParserHandler()
        db = Database()
        for f in p.glob("*.gpx"):
            ai_object = db.get_autoimport_by_trackfile(str(f.absolute()))
            if not ai_object:
                files_to_import.append(f)

        self._total_to_import = len(files_to_import)
        self.emit("total-files-to-autoimport", int(self._total_to_import))
        for f in files_to_import:
            result = parser.parse(str(f))
            self._import_track(result)

    def _import_finished(self, result: Result):
        if result.is_ok:
            self._imported = self._imported + 1
        else:
            self._not_imported = self._not_imported + 1

        self._insert_autoimport_info(result.filename, result.code)

        total = self._imported + self._not_imported
        if total == self._total_to_import and self._imported > 0:
            GLib.idle_add(self._callback)

    def _insert_autoimport_info(self, pathfile, code):
        """Add information about imported file into database.

        Arguments:
        pathfile -- the original track file that was tried to import.
        code -- the Result.code value.
        """
        db = Database()
        auto_import = AutoImport(
            None,
            path.join(self._folder, Path(pathfile).name),
            code
        )
        db.insert(auto_import)


class ParserHandler:
    """Handler the GPX parser task."""

    def parse(self, filename):
        try:
            if filename.endswith(".gpx"):
                parser = GpxParser()
                xmlparser = XMLParser(target=parser)
                with open(filename, "rb") as file:
                    for data in file:
                        xmlparser.feed(data)
                    xmlparser.close()
            elif filename.endswith(".fit"):
                parser = FitParser(filename)
                parser.parse()
            else:
                raise Exception(f"invalid file to parse: {filename}")

            if not parser.track:
                raise Exception("empty track")

            tp = parser.track.track_points
            if not tp or len(tp) == 0:
                raise Exception("empty track")

            return Result(
                code=Result.OK,
                track=parser.track,
                filename=filename,
                recorded_with=parser.recorded_with
            )
        except Exception as error:
            message = f"Error parsing the file {filename}: {error}"
            pyot_logging.get_logger(__name__).exception(message)
            return Result(
                code=Result.ERROR,
                filename=filename,
                message=message
            )


class ParserHandlerInThread(GObject.GObject):
    """Handle the parser task into a thread."""

    __gsignals__ = {
        "end-parse": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._filename = None
        self._callback = None

    def parse(self, filename, callback):
        """Parse the filename.
        Arguments:
        filename -- the filename to be parsed.
        callback -- a function that accept a dictionary with the
                    following keys:
                    - file: path's file.
                    - track: Track object or None if any error.
                    - error: message's error or None.
        """
        self._filename = filename
        self._callback = callback
        thread = threading.Thread(target=self._parse_in_thread)
        thread.daemon = True
        thread.start()

    def _parse_in_thread(self):
        try:
            if self._filename.endswith(".gpx"):
                parser = GpxParser()
                xmlparser = XMLParser(target=parser)
                with open(self._filename, 'rb') as file:
                    for data in file:
                        xmlparser.feed(data)
                    xmlparser.close()
            elif self._filename.endswith(".fit"):
                parser = FitParser(self._filename)
                parser.parse()
            else:
                raise Exception(f"invalid file to parse: {self._filename}")

            self.emit("end-parse")

            if not parser.track:
                raise Exception("empty track")

            tp = parser.track.track_points
            if not tp or len(tp) == 0:
                raise Exception("empty track")

            GLib.idle_add(
                self._callback,
                Result(
                    code=Result.OK,
                    filename=self._filename,
                    track=parser.track,
                    recorded_with=parser.recorded_with
                )
            )
        except Exception as error:
            message = f"Error parsing the file {self._filename}: {error}"
            pyot_logging.get_logger(__name__).exception(message)
            GLib.idle_add(
                self._callback,
                Result(
                    code=Result.ERROR,
                    filename=self._filename,
                    message=message
                )
            )
