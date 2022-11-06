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
from pathlib import Path
from typing import Generator

from pyopentracks.io.importer.importer import ImportResult, Importer
from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.parser.records import Record
from pyopentracks.io.proxy.proxy import RecordProxy
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils import logging as pyot_logging


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
            try:
                record = ParserFactory.make(str(f)).parse()
                self._import(str(f), record)
            except Exception as error:
                message = f"Error parsing the file {str(f)}: {error}"
                pyot_logging.get_logger(__name__).exception(message)
                self._result.errors.append(message)
            yield self._result

    def _import(self, filename: str, record: Record):
        if not record or record.type not in (Record.Type.TRACK, Record.Type.SET):
            self._result.errors.append(
                _(f"Error importing the file {filename}: it could not be parsed: there are not segments or sets")
            )
            return

        activity = RecordProxy(record).to_activity()
        if DatabaseHelper.get_existed_activities(activity):
            self._result.errors.append(
                _(f"Error importing the file {filename}: activity '{activity.name}' already exists")
            )
            return

        if record.type == Record.Type.TRACK:
            activity_id = DatabaseHelper.insert_track_activity(activity)
        else:
            sets = RecordProxy(record).to_sets()
            activity_id = DatabaseHelper.insert_set_activity(activity, sets)

        if activity_id is None:
            message = _(
                f"Error importing the file {filename}."
                f"\nIt couldn't be inserted in the database."
            )
            pyot_logging.get_logger(__name__).debug(message)
            self._result.errors.append(message)
        else:
            self._result.imported += 1
