"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>

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
import shutil

from os import path
from pathlib import Path

from gi.repository import GLib, GObject

from pyopentracks.io.gpx_parser import GpxParserHandler
from pyopentracks.models.database import Database
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.auto_import import AutoImport
from pyopentracks.settings import imported_tracks_folder
from pyopentracks.io.result import Result


class ImportHandler():
    def __init__(self):
        self._callback = None

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
            result = Result(code=Result.ERROR, filename=import_result.filename, message=import_result.message)
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
                        filename=track.trackfile_path,
                        message=_("Track already exists")
                    )
                else:
                    # Track doesn't exists -> make importing.
                    result = self._import(track)

            except Exception as error:
                result = Result(code=Result.ERROR, filename=track.trackfile_path, message=str(error))

        self._import_finished(result)

    def _copy_file(self, path_str):
        """Copy the file to internal data.

        Copy the file in the path path_str to the internal folder
        where all tracks are located.

        It avoid collision looking for a name not used in all the
        folder.

        Arguments:
        path_str -- the string representing the path of the file
                    to be copied.

        Return:
        The string path of the destination file or None if copy was
        not possible.
        """
        path_src = Path(path_str)
        path_dst = Path(path.join(imported_tracks_folder(), path_src.name))
        i = 0
        while path_dst.exists():
            newname = path_dst.stem + "." + str(i) + path_dst.suffix
            path_dst = Path(path.join(imported_tracks_folder(), newname))
            i = i + 1
        try:
            shutil.copy(path_src.absolute(), path_dst.absolute())
        except Exception as error:
            # TODO move this to logger.
            print(f"Error: shutil copy error: {error}")
            return None
        return str(path_dst.absolute())

    def _clean_file(self, path_str):
        shutil.remove(path_str)

    def _import(self, track):
        """Makes the importing of the track.

        It copies the track file and then insert the track and its track points
        to the database.

        This method assumes track can be inserted in the database.

        Arguments:
        track -- Track object to be inserted in the database.

        Return:
        Result object.
        """
        code = Result.ERROR
        message = _(f"File {track.trackfile_path} couldn't be copied to internal storage"),

        dst_path = self._copy_file(track.trackfile_path)
        if dst_path:
            track.set_trackfile_path(dst_path)
            trackid = DatabaseHelper.insert(track)
            if not trackid:
                shutil.remove(dst_path)
            else:
                DatabaseHelper.bulk_insert(track.track_points, trackid)

            code = Result.OK if trackid else Result.ERROR
            message = _("Track imported") if trackid else _(f"Error importing the file {track.trackfile_path}.\nIt couldn't be inserted in the database")

        return Result(code=code, track=track, filename=track.trackfile_path, message=message)


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
        parser = GpxParserHandler()
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
        self._files_name = []
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

    def import_folder(self, path: str, cb):
        self._result["folder"] = path
        p = Path(self._result["folder"])
        self._files_name = [f for f in p.glob("*.gpx")]
        self._result["total"] = len(self._files_name)
        self.emit("total-files-to-import", int(self._result["total"]))
        self._callback = cb

        self._thread = threading.Thread(target=self._import_in_thread, daemon=True)
        self._thread.start()

    def _import_in_thread(self):
        parser = GpxParserHandler()
        for f in self._files_name:
            result = parser.parse(f)
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
        parser = GpxParserHandler()
        db = Database()
        for f in p.glob("*.gpx"):
            ai_object = db.get_autoimport_by_trackfile(str(f.absolute()))
            if not ai_object:
                files_to_import.append(f)

        self._total_to_import = len(files_to_import)
        self.emit("total-files-to-autoimport", int(self._total_to_import))
        for f in files_to_import:
            result = parser.parse(f)
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
        pathfile -- the origial track file that was tried to import.
        code -- the Result.code value.
        """
        db = Database()
        auto_import = AutoImport(
            None,
            path.join(self._folder, Path(pathfile).name),
            code
        )
        db.insert(auto_import)
