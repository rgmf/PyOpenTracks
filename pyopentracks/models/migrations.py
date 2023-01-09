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
            CREATE TABLE stats (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                elevationloss FLOAT,
                maxhr FLOAT,
                avghr FLOAT,
                maxcadence FLOAT,
                avgcadence FLOAT,
                normalizedpower FLOAT,
                maxpower FLOAT,
                mintemperature FLOAT,
                maxtemperature FLOAT,
                avgtemperature FLOAT,
                totalcalories INTEGER,
                FOREIGN KEY (_id) REFERENCES activities (statsid) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)

        query = """
            CREATE TABLE activities (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid BLOB,
                name TEXT,
                description TEXT,
                category TEXT,
                recorded_with INTEGER,
                starttime INTEGER,
                statsid INTEGER,
                FOREIGN KEY (statsid) REFERENCES stats (_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)
        query = "CREATE UNIQUE INDEX activities_uuid_index ON activities (uuid)"
        query = "CREATE UNIQUE INDEX activities_stats_id_index ON activities (statsid)"
        self._db.execute(query)

        query = """
            CREATE TABLE sections (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                activityid INTEGER,
                FOREIGN KEY (activityid) REFERENCES activities (_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)
        query = "CREATE INDEX sections_activityid_index ON sections (activityid)"
        self._db.execute(query)

        query = """
            CREATE TABLE trackpoints (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                sectionid INTEGER NOT NULL,
                longitude INTEGER NOT NULL,
                latitude INTEGER NOT NULL,
                time INTEGER NOT NULL,
                speed FLOAT,
                altitude FLOAT,
                gain FLOAT,
                loss FLOAT,
                heartrate FLOAT,
                cadence FLOAT,
                power FLOAT,
                temperature FLOAT,
                FOREIGN KEY (sectionid) REFERENCES sections (_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)
        query = "CREATE INDEX trackpoints_sectionid_index ON trackpoints (sectionid)"
        self._db.execute(query)

        query = """
            CREATE TABLE sets (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                type INTEGER,
                result INTEGER,
                exercisecategory INTEGER,
                weight FLOAT,
                repetitions INT,
                avghr FLOAT,
                maxhr FLOAT,
                time INTEGER,
                calories INTEGER,
                temperature FLOAT,
                difficulty INTEGER,
                statsid INTEGER,
                FOREIGN KEY (statsid) REFERENCES stats (_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)
        query = "CREATE INDEX sets_statsid_index ON sets (statsid)"
        self._db.execute(query)

        query = """
            CREATE TABLE segments (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                distance FLOAT NOT NULL,
                gain FLOAT NOT NULL,
                loss FLOAT NOT NULL
            );
        """
        self._db.execute(query)

        query = """
            CREATE TABLE segmentpoints (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                segmentid INTEGER NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                altitude FLOAT,
                FOREIGN KEY (segmentid) REFERENCES segments (_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """
        self._db.execute(query)
        query = "CREATE INDEX segmentpoints_segmentid_index ON segmentpoints (segmentid)"
        self._db.execute(query)

        query = """
            CREATE TABLE segmentracks (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                segmentid INTEGER NOT NULL,
                activityid INTEGER NOT NULL,
                trackpointid_start INTEGER NOT NULL,
                trackpointid_end INTEGER NOT NULL,
                time INTEGER NOT NULL,
                maxspeed FLOAT,
                avgspeed FLOAT,
                maxhr FLOAT,
                avghr FLOAT,
                maxcadence FLOAT,
                avgcadence FLOAT,
                avgpower FLOAT,
                FOREIGN KEY (segmentid) REFERENCES segments (_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (activityid) REFERENCES activities (_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (trackpointid_start) REFERENCES trackpoints (_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (trackpointid_end) REFERENCES trackpoints (_id) ON UPDATE CASCADE ON DELETE CASCADE                
            );
        """
        self._db.execute(query)
        query = "CREATE INDEX segmenttracks_segmentid_index ON segmentracks (segmentid)"
        self._db.execute(query)
        query = "CREATE INDEX segmenttracks_activityid_index ON segmentracks (activityid)"
        self._db.execute(query)
        query = "CREATE INDEX segmenttracks_trackpointid_start_index ON segmentracks (trackpointid_start)"
        self._db.execute(query)
        query = "CREATE INDEX segmenttracks_trackpointid_end_index ON segmentracks (trackpointid_end)"
        self._db.execute(query)

        query = """
            CREATE TABLE autoimport (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                activityfile TEXT,
                result INTEGER
            );
        """
        self._db.execute(query)
        query = "CREATE UNIQUE INDEX autoimport_activityfile_index ON autoimport (activityfile)"
        self._db.execute(query)
