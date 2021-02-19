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

import sqlite3
from os import path, makedirs

from ..settings import xdg_data_home


class Database:
    """SQLite database handler."""

    def __init__(self):
        makedirs(path.dirname(self._db_file), exist_ok=True)
        self._conn = sqlite3.connect(self._db_file)

    @property
    def _db_file(self) -> str:
        return path.join(self._db_dir, "database.db")

    @property
    def _db_dir(self) -> str:
        return xdg_data_home()

    def execute(self, query: str):
        """Executes the raw query without return any results.

        It can be used to create, alter... or all queries that not need
        results returned.
        """
        try:
            self._conn.execute(query)
            self._conn.commit()
        except Exception as error:
            # TODO add this error message to a logger system
            print(f"Error: [SQL] Couldn't execute the query: {error}: {query}")
