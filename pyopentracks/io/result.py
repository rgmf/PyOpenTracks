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


class Result:
    OK = 0
    ERROR = 1
    EXISTS = 2

    def __init__(self, code, track=None, filename=None, message=None):
        self._code = code
        self._track = track
        self._filename = filename
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def track(self):
        return self._track

    @property
    def filename(self):
        if not self._filename:
            return _("file name unknown")
        return self._filename

    @property
    def message(self):
        if not self._message:
            return ""
        return self._message

    @property
    def is_ok(self):
        return self._code == Result.OK
