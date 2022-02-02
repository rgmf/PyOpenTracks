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

from enum import Enum


class RecordedWith(Enum):
    """Enum with recorded devices possibilities."""

    UNKNOWN = 0
    OPENTRACKS = 1


class Result:
    """Result for importing tracks."""

    OK = 0
    ERROR = 1
    EXISTS = 2

    def __init__(
        self, code, track=None, filename=None, message=None, recorded_with=None
    ):
        """Create a Result object with a code at least."""
        self._code = code
        self._track = track
        self._filename = filename
        self._message = message
        self._recorded_with = recorded_with

    @property
    def code(self):
        """Return code property."""
        return self._code

    @property
    def track(self):
        """Return track object."""
        return self._track

    @property
    def filename(self):
        """Return name of the file imported."""
        if not self._filename:
            return "unknown"
        return self._filename

    @property
    def is_ok(self):
        """Return True if importing was ok."""
        return self._code == Result.OK

    @property
    def message(self):
        """Return the message if any. Otherwise return empty string."""
        return self._message if self._message is not None else ""

    @property
    def recorded_with(self):
        """Return RecordedWith enumeration value for recorded_with."""
        return RecordedWith.UNKNOWN if self._recorded_with is None\
          else self._recorded_with
