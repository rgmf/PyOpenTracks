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

from gi.repository import GLib, GObject
from pyopentracks.io.importer.factory import ImporterFactory


class ImportHandler(GObject.GObject):

    __gsignals__ = {
        "total-files-to-import": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)
        self._callback = None
        self._thread = None
        self._importer = None

    def stop(self):
        if self._thread:
            self._thread.do_run = False

    def import_folder(self, filename: str, cb):
        self._importer = ImporterFactory.make(filename)
        total_files = self._importer.files_to_import()

        self.emit("total-files-to-import", total_files)
        self._callback = cb

        self._thread = threading.Thread(target=self._import_in_thread, daemon=True)
        self._thread.start()

    def _import_in_thread(self):
        for result in self._importer.run():
            self._result = result
            if not getattr(self._thread, "do_run", True):
                break
            GLib.idle_add(self._callback, result)
