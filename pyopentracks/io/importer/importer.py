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
from pathlib import Path

from pyopentracks.io.parser.records import Record, TrackRecord, SetRecord, MultiRecord
from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.proxy.proxy import RecordProxy
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils import logging as pyot_logging


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


class FileImporter(Importer):

    def __init__(self, filename: str):
        super().__init__(filename)

    def files_to_import(self) -> int:
        return 1

    def run(self) -> Generator[ImportResult, None, None]:
        try:
            record = ParserFactory.make(self._filename).parse()
            yield self._import(record)
        except Exception as error:
            message = f"Error parsing the file {self._filename}: {error}"
            pyot_logging.get_logger(__name__).exception(message)
            yield ImportResult(filename=self._filename, total=1, imported=0, errors=[message])

    def _import(self, record: Record):
        if not record or (
                not isinstance(record, TrackRecord) and
                not isinstance(record, SetRecord) and
                not isinstance(record, MultiRecord)
        ):
            return ImportResult(
                record=record,
                filename=self._filename,
                total=1,
                imported=0,
                errors=[_(
                    f"Error importing the file {self._filename}: "
                    "it could not be parsed: there are not segments, sets or multi record"
                )]
            )

        activity = RecordProxy(record).to_activity()
        if DatabaseHelper.get_existed_activities(activity):
            return ImportResult(
                record=record,
                filename=self._filename,
                total=1,
                imported=0,
                errors=[_(
                    f"Error importing the file {self._filename}: "
                    f"activity '{activity.name}' already exists"
                )]
            )

        if isinstance(record, TrackRecord):
            activity_id = DatabaseHelper.insert_track_activity(activity)
        elif isinstance(record, SetRecord):
            sets = RecordProxy(record).to_sets()
            activity_id = DatabaseHelper.insert_set_activity(activity, sets)
        else:
            activity_id = DatabaseHelper.insert_multi_activity(activity)
            for r in record.records:
                if isinstance(r, TrackRecord):
                    activity = RecordProxy(r).to_activity()
                    activity.activity_id = activity_id
                    DatabaseHelper.insert_track_activity(activity)
                elif isinstance(r, SetRecord):
                    activity = RecordProxy(r).to_activity()
                    activity.activity_id = activity_id
                    sets = RecordProxy(record).to_sets()
                    DatabaseHelper.insert_set_activity(activity, sets)

        if activity_id is None:
            return ImportResult(
                record=record,
                filename=self._filename,
                total=1,
                imported=0,
                errors=[_(
                    f"Error importing the file {self._filename}."
                    f"\nIt couldn't be inserted in the database."
                )]
            )
        else:
            return ImportResult(
                record=record,
                filename=self._filename,
                total=1,
                imported=1
            )


class FolderImporter(Importer):

    def __init__(self, foldername: str):
        super().__init__(foldername)

        # Select all GPX and FIT files from path folder.
        path_object = Path(self._filename)
        self._files_path = [f for f in path_object.glob("*.gpx")]
        self._files_path.extend([f for f in path_object.glob("*.fit")])

        # Initialize ImportResult with folder name and total files to import.
        self._result: ImportResult = ImportResult()
        self._result.filename = foldername
        self._result.total = len(self._files_path)

    def files_to_import(self) -> int:
        return self._result.total

    def run(self) -> Generator[ImportResult, None, None]:
        for f in self._files_path:
            result = next(FileImporter(str(f)).run())
            if result.is_ok:
                self._result.imported += 1
            else:
                self._result.errors.append(result.errors[0])
            yield self._result
