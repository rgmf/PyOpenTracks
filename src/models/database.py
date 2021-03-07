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
from os import path

from pyopentracks.settings import xdg_data_home
from pyopentracks.models.track import Track


class Database:
    """SQLite database handler."""

    def __init__(self):
        #makedirs(path.dirname(self._db_file), exist_ok=True)
        #self._conn = sqlite3.connect(self._db_file)
        pass

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
        with sqlite3.connect(self._db_file) as conn:
            try:
                conn.execute(query)
                conn.commit()
            except Exception as error:
                # TODO add this error message to a logger system
                print(
                    f"Error: [SQL] Couldn't execute the query: "
                    f"{error}: {query}"
                )

    def get_track_by_id(self, _id):
        """Return Track object from _id.

        Arguments:
        _id -- id of the track to look up in the database.

        Return:
        Track object or None if there is any Track identified by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM tracks WHERE _id=?"
                tuple_result = conn.execute(query, (_id,)).fetchone()
                if tuple_result:
                    return Track(*tuple_result)
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return None

    def get_track_by_autoimport_file(self, path: str):
        """Return Track object from autoimportfile.

        Arguments:
        path -- the path of the file to auto-import.

        Return:
        Track object or None if there is any Track with path.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM tracks WHERE autoimportfile=?"
                tuple_result = conn.execute(query, (path,)).fetchone()
                if tuple_result:
                    return Track(*tuple_result)
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return None

    def get_tracks(self):
        """Get all tracks from database.

        Return:
        list of Track object sorted by start time.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM tracks ORDER BY starttime DESC"
                return [
                    Track(*track) for track in conn.execute(query).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

    def get_existed_tracks(self, uuid, start, end):
        """"Look for a Track from arguments.

        Look for a track that has the same uuid or has the same start and
        end time.

        Arguments:
        uuid -- UUID that could be None.
        start -- start time in milliseconds.
        end -- end time in milliseconds.

        Return:
        list of tracks or None.

        Raise:
        raise the exception could be triggered.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                SELECT * FROM tracks
                WHERE uuid=? OR (starttime=? and stoptime=?)
                """
                tracks = conn.execute(query, (uuid, start, end)).fetchall()
                if tracks:
                    return [Track(*track) for track in tracks]
                return None
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
                raise

    def insert(self, model):
        """Insert the model in the database.

        Arguments:
        model -- Model object to be inserted.

        Return:
        last row id or None if any model was inserted.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(model.insert_query, model.fields)
                conn.commit()
                return cursor.lastrowid
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
        return None
