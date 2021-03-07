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
from pyopentracks.settings import imported_tracks_folder


class ImportHandler():
    OK = 1
    ERROR = 2
    EXISTS = 3

    def __init__(self):
        self._callback = None

    def _import_finished(self, result):
        raise NotImplementedError

    def _import_track(self, import_result):
        """Import track if not exists.

        This method is called when parsing is finished and it checks
        if track exists for importing it or not.

        Arguments:
        import_result -- a dictionary with the following keys:
                         - file: path's file.
                         - track: Track object or None if any error.
                         - error: message's error or None.
        """
        if not import_result["track"]:
            result = {
                "file": import_result["file"],
                "import": ImportHandler.ERROR,
                "message": import_result["message"]
            }
        else:
            track = import_result["track"]
            try:
                db = Database()
                tracks = db.get_existed_tracks(
                    track.uuid, track.start_time_ms, track.end_time_ms
                )
                if tracks:
                    # Track exists
                    result = {
                        "file": track.trackfile_path,
                        "import": ImportHandler.EXISTS,
                        "message": _("Track already exists")
                    }
                else:
                    # Track doesn't exists -> make importing.
                    result = self._import(track)

            except Exception as error:
                result = {
                    "file": track.trackfile_path,
                    "import": ImportHandler.ERROR,
                    "message": str(error)
                }

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

        It copies the track file and then insert the track to the database.
        This method assumes track can be inserted in the database.

        Arguments:
        track -- Track object to be inserted in the database.

        Return:
        A dictionary with import, message and tracks to None.
        """
        import_res = ImportHandler.ERROR
        message = _(f"File {track.trackfile_path} couldn't be copied to internal storage"),

        dst_path = self._copy_file(track.trackfile_path)
        if dst_path:
            db = Database()
            track.set_trackfile_path(dst_path)
            trackid = db.insert(track)
            if not trackid:
                shutil.remove(dst_path)

            import_res = ImportHandler.OK if trackid else ImportHandler.ERROR
            message = _("Track imported") if trackid else _(f"Error importing the file {track.trackfile_path}.\nIt couldn't be inserted in the database")

        return {
            "file": track.trackfile_path,
            "import": import_res,
            "message": message
        }


class ImportFileHandler(ImportHandler):

    def __init__(self):
        super().__init__()
        self._filename = None

    def import_file(self, path: str, cb):
        """Parse the filename and import it if needed.

        Arguments:
        path -- the filename to be parsed.
        callback -- a function that accept Track object to be
                    called when parsing and importing is finished.
                    It's a function used to get the result of the
                    parsing and importing process.
        """
        self._filename = path
        self._callback = cb
        thread = threading.Thread(target=self._import_in_thread)
        thread.daemon = True
        thread.start()

    def _import_in_thread(self):
        parser = GpxParserHandler()
        result = parser.parse(self._filename)
        self._import_track(result)

    def _import_finished(self, result: dict):
        GLib.idle_add(self._callback, result)


class ImportFolderHandler(ImportHandler, GObject.GObject):

    __gsignals__ = {
        "total-files-to-import": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        "end-import-file": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)
        self._callback = None
        self._result = {
            "folder": "",
            "total": 0,
            "imported": 0,
            "errors": []
        }

    def import_folder(self, path: str, cb):
        self._result["folder"] = path
        self._callback = cb
        thread = threading.Thread(target=self._import_in_thread)
        thread.daemon = True
        thread.start()

    def _import_in_thread(self):
        p = Path(self._result["folder"])
        files_name = [f for f in p.glob("*.gpx")]
        self._result["total"] = len(files_name)
        self.emit("total-files-to-import", int(self._result["total"]))
        parser = GpxParserHandler()
        for f in files_name:
            result = parser.parse(f)
            self._import_track(result)

    def _import_finished(self, result: dict):
        if result["import"] == ImportHandler.OK:
            self._result["imported"] = self._result["imported"] + 1
        else:
            self._result["errors"].append(
                _(f"Error importing the file {result['file']}: {result['message']}")
            )

        total_imported = (
            self._result["imported"] + len(self._result["errors"])
        )
        self.emit("end-import-file", total_imported)
        if self._result["total"] == total_imported:
            GLib.idle_add(self._callback, self._result)


class AutoImportHandler(ImportHandler):

    def __init__(self):
        super().__init__()
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
            track = db.get_track_by_autoimport_file(str(f.absolute()))
            if not track:
                files_to_import.append(f)

        self._total_to_import = len(files_to_import)
        for f in files_to_import:
            result = parser.parse(f)
            self._import_track(result)

    def _import(self, track):
        """Inject autoimportfile value to the track before importing."""
        filename = Path(track.trackfile_path).name
        track.set_autoimportfile_path(path.join(self._folder, filename))
        return super()._import(track)

    def _import_finished(self, result: dict):
        if result["import"] == ImportHandler.OK:
            self._imported = self._imported + 1
        else:
            self._not_imported = self._not_imported + 1

        total = self._imported + self._not_imported
        if total == self._total_to_import and self._imported > 0:
            GLib.idle_add(self._callback)
