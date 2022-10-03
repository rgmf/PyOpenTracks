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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, List

from pyopentracks.io.parser.records import Record


@dataclass
class ImportResult:
    # record data getting from parsing
    record: Record = None
    # it can be a folder or a file
    filename: str = ""
    # number of files to import
    total: int = 0
    # number of files correctly imported
    imported: int = 0
    # list of messages errors. To access all errors you should call get_errors property
    errors: List[str] = field(default_factory=lambda: [])

    @property
    def total_imported(self):
        return self.imported + len(self.errors)

    @property
    def is_done(self):
        return self.imported + len(self.errors) == self.total

    @property
    def is_ok(self):
        return self.total == self.imported

    @property
    def is_error(self):
        return len(self.errors) > 0


class Importer(ABC):

    def __init__(self, file: str):
        self._filename = file        

    @abstractmethod
    def files_to_import(self) -> int:
        pass

    @abstractmethod
    def run(self) -> Generator[ImportResult, None, None]:
        pass
