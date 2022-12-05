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

from dataclasses import dataclass
from enum import Enum

from pyopentracks.io.parser.records import Record


class ResultCode(Enum):
    UNKNOWN = -1
    OK = 0
    ERROR = 1
    EXISTS = 2


@dataclass
class Result:
    """Result for importing activities."""

    code: ResultCode = ResultCode.UNKNOWN
    record: Record = Record()
    filename: str = "Unknown"
    message: str = ""

    @property
    def is_ok(self):
        """Return True if importing was ok."""
        return self.code == ResultCode.OK

    @property
    def is_error(self):
        return not self.is_ok()
