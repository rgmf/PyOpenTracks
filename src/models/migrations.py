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


class Migration:
    """This class handle migrations.

    If you want to do database schema changes then follow these steps:
    1.- Add one to DB_VERSION.
    2.- Creates a new method with the query to be executed and call
        self._db.execute with that query.
    3.- Add a new if in the migrate method that call the method
        created in the step 2.
    """
    DB_VERSION = 1

    def __init__(self, db, db_version):
        self._db = db
        self._db_version = db_version

    def migrate(self):
        if Migration.DB_VERSION != self._db_version:
            if Migration.DB_VERSION == 1:
                self._migrate_1()
        return Migration.DB_VERSION

    def _migrate_1(self):
        query = """
        CREATE TABLE tracks (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        trackfile TEXT,
        uuid BLOB,
        name TEXT,
        description TEXT,
        category TEXT,
        starttime INTEGER,
        stoptime INTEGER,
        totaldistance FLOAT,
        totaltime INTEGER,
        movingtime INTEGER,
        avgspeed FLOAT,
        avgmovingspeed FLOAT,
        maxspeed FLOAT,
        minelevation FLOAT,
        maxelevation FLOAT,
        elevationgain FLOAT,
        elevationloss FLOAT
        );
        """
        self._db.execute(query)
        query = "CREATE UNIQUE INDEX tracks_uuid_index ON tracks (uuid)"
        self._db.execute(query)
        query = "CREATE UNIQUE INDEX trackfile_index ON tracks (trackfile)"
        self._db.execute(query)

        query = """
        CREATE TABLE autoimport (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        trackfile TEXT,
        result INTEGER
        );
        """
        self._db.execute(query)
        query = "CREATE UNIQUE INDEX autoimport_trackfile_index ON autoimport (trackfile)"
        self._db.execute(query)
