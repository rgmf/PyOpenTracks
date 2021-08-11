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
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.models.auto_import import AutoImport
from pyopentracks.models.aggregated_stats import AggregatedStats


class Database:
    """SQLite database handler."""

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

    def get_aggregated_stats(self, date_from=None, date_to=None):
        """Query for aggregated stats.

        Arguments:
        date_from -- (optional) milliseconds to filter dates from.
        date_to -- (optional) milliseconds to filter dates to.

        Return:
        the aggregated stats model.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                if date_from and date_to:
                    where = f"""
                    WHERE starttime>={date_from} and starttime<={date_to}
                    """
                elif date_from:
                    where = f"WHERE starttime>={date_from}"
                elif date_to:
                    where = f"WHERE starttime<={date_to}"
                else:
                    where = ""

                query = f"""
                SELECT
                category,
                COUNT(*) total_activities,
                SUM(totaltime) total_time,
                SUM(movingtime) total_moving_time,
                SUM(totaldistance) total_distance,
                SUM(elevationgain) total_gain,
                AVG(totaltime) avg_time,
                AVG(movingtime) avg_moving_time,
                AVG(totaldistance) avg_distance,
                AVG(elevationgain) avg_gain,
                SUM(totaldistance) / (SUM(movingtime) / 1000) avg_speed,
                AVG(avghr) avg_heart_rate,
                MAX(totaltime) max_time,
                MAX(movingtime) max_moving_time,
                MAX(totaldistance) max_distance,
                MAX(elevationgain) max_gain,
                MAX(maxspeed) max_speed,
                MAX(maxhr) max_heart_rate
                FROM tracks
                {where}
                GROUP BY category
                ORDER BY total_activities DESC;
                """

                stats = conn.execute(query).fetchall()
                if stats:
                    return [AggregatedStats(*s) for s in stats]
                return None
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
                raise

    def get_years(self):
        """Returns all years where there are activities.

        Return
        List of years.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                SELECT distinct strftime('%Y', starttime / 1000, 'unixepoch')
                FROM tracks
                ORDER BY starttime DESC
                """
                items = conn.execute(query).fetchall()
                if items:
                    return [i[0] for i in items]
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
        return []

    def get_track_points(self, trackid):
        """Get all track points from track identified by trackid.

        Arguments:
        trackid -- Track's id.

        Return:
        list of all TrackPoint objects that hast the Track identified
        by trackid.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                SELECT *
                FROM trackpoints
                WHERE trackid=?
                ORDER BY _id ASC
                """
                trackpoints = conn.execute(query, (trackid,)).fetchall()
                if trackpoints:
                    return [TrackPoint(*tp) for tp in trackpoints]
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
        return []

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

    def delete(self, model):
        """Delete the model from the database.

        Arguments:
        model -- Model object to be deleted.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                # SQLite foreign keys are disabled for compatibility purposes.
                # You need to enable them manually right after each connection to the database.
                conn.execute("PRAGMA foreign_keys = ON")
                cursor.execute(model.delete_query, (model.id,))
                conn.commit()
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)

    def update(self, model):
        """Update the model in the database.

        Arguments:
        model -- Model object to be updated.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                # SQLite foreign keys are disabled for compatibility purposes.
                # You need to enable them manually right after each connection to the database.
                conn.execute("PRAGMA foreign_keys = ON")
                cursor.execute(model.update_query, model.update_data)
                conn.commit()
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)

    def get_autoimport_by_trackfile(self, pathfile: str):
        """Return AutoImport object from trackfile.

        Arguments:
        pathfile -- the path of the file.

        Return:
        AutoImport object or None if there is any AutoImport with path.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM autoimport WHERE trackfile=?"
                tuple_result = conn.execute(query, (pathfile,)).fetchone()
                if tuple_result:
                    return AutoImport(*tuple_result)
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return None
