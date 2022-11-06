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
from typing import Generator
from pyopentracks.io.importer.importer import ImportResult, Importer
from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.parser.records import Record
from pyopentracks.io.proxy.proxy import RecordProxy
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils import logging as pyot_logging


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
        if not record or record.type not in (Record.Type.TRACK, Record.Type.SET):
            return ImportResult(
                record=record,
                filename=self._filename,
                total=1,
                imported=0,
                errors=[_(
                    f"Error importing the file {self._filename}: it could not be parsed: there are not segments or sets"
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
                    f"Error importing the file {self._filename}: activity '{activity.name}' already exists"
                )]
            )

        if record.type == Record.Type.TRACK:
            activity_id = DatabaseHelper.insert_track_activity(activity)
        else:
            sets = RecordProxy(record).to_sets()
            activity_id = DatabaseHelper.insert_set_activity(activity, sets)

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
