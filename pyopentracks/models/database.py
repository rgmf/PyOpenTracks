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
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.models.segment import Segment
from pyopentracks.models.segment_point import SegmentPoint


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

    def get_tracks_between(self, begin, end):
        """Returns all tracks between begin date and end date.

        Arguments:
        begin -- begin's date in milliseconds.
        end   -- end's date in milliseconds.

        Returns:
        List of tracks between begin and end.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM tracks WHERE starttime>=? AND starttime<=?"
                return [Track(*t) for t in conn.execute(query, (begin, end)).fetchall()]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []


    def get_segment_by_id(self, _id):
        """Return Segment object from _id.

        Arguments:
        _id -- id of the segment to look up in the database.

        Return:
        Segment object or None if there is any Track identified by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM segments WHERE _id=?"
                tuple_result = conn.execute(query, (_id,)).fetchone()
                if tuple_result:
                    return Segment(*tuple_result)
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return None

    def get_segment_tracks_by_trackid(self, trackid):
        """Return segmentracks from track's id."""
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                    SELECT * 
                    FROM segmentracks 
                    WHERE trackid=?
                    ORDER BY _id
                """
                return [
                    SegmentTrack(*st) for st in conn.execute(query, (trackid,)).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

    def get_segment_tracks_by_segmentid(self, segmentid):
        """Return segmentracks from segment's id."""
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                    SELECT * 
                    FROM segmentracks 
                    WHERE segmentid=?
                    ORDER BY time ASC
                """
                return [
                    SegmentTrack(*st) for st in conn.execute(query, (segmentid,)).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

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

    def get_tracks_with_near_point_start(self, bbox, trackid=None):
        """Look for points inside trackpoints table that are inside the bounding box bbox.

        Arguments:
        bbox    -- the BoundingBox's object (north, east, south and west Locations).
        trackid -- (optional) track's id where looking for points.

        Returns:
        list of SegmentTrack.Point with all points inside p1, p2, p3 and p4 bounding box.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                where = f" trackid = {trackid} AND " if trackid else ""
                query = f"""
                    SELECT
                        trackid,
                        _id,
                        latitude,
                        longitude,
                        strftime('%Y%m%d%H%M', time / 1000, 'unixepoch') datetimetominutes
                    FROM
                        trackpoints
                    WHERE
                        {where}
                        latitude > {bbox.south.latitude} AND
                        latitude < {bbox.north.latitude} AND
                        longitude < {bbox.east.longitude} AND
                        longitude > {bbox.west.longitude}
                    GROUP BY datetimetominutes
                    ORDER BY trackid DESC, _id ASC
                """
                return [
                    SegmentTrack.Point(*row) for row in conn.execute(query).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

    def get_tracks_with_near_point_end(self, bbox, trackid, trackpoint_id_from):
        """Look for points inside tracks identify by trackid that are inside the bounding box bbox.

        Only trackpoints identify by an id greater than trackpoint_id_from.

        Arguments:
        bbox               -- the BoundingBox's object (north, east, south and west Locations).
        trackid            -- track id where it'll look for points inside p1, p2, p3 and p4.
        trackpoint_id_from -- trackpoints id from it'll look for points inside p1, p2, p3 and p4.

        Returns:
        The recorded SegmentTrack.Point sooner inside p1, p2, p3 and p4.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"""
                    SELECT
                        trackid,
                        _id,
                        latitude,
                        longitude,
                        MIN(time)
                    FROM
                        trackpoints
                    WHERE
                        trackid = {trackid} AND
                        _id > {trackpoint_id_from} AND
                        latitude > {bbox.south.latitude} AND
                        latitude < {bbox.north.latitude} AND
                        longitude < {bbox.east.longitude} AND
                        longitude > {bbox.west.longitude}
                    GROUP BY time
                    ORDER BY _id ASC
                """
                tuple_result = conn.execute(query).fetchone()
                return SegmentTrack.Point(*tuple_result) if tuple_result else None
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

    def get_aggregated_stats(self, date_from=None, date_to=None, order_by="total_activities"):
        """Query for aggregated stats.

        Arguments:
        date_from -- (optional) milliseconds to filter dates from.
        date_to -- (optional) milliseconds to filter dates to.
        order_by -- (optional) name of the column that will be used to order the results.

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
                ORDER BY {order_by} DESC;
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
                query = "SELECT * FROM trackpoints WHERE trackid=? ORDER BY _id ASC"
                trackpoints = conn.execute(query, (trackid,)).fetchall()
                if trackpoints:
                    return [TrackPoint(*tp) for tp in trackpoints]
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
        return []

    def get_track_points_between(self, trackpoint_from_id, trackpoint_to_id):
        """Get all track points from trackpoint_from_id to trackpoint_to_id.

        Arguments:
        trackpoint_from_id -- TrackPoint's beginning id.
        trackpoint_to_id   -- TrackPoint's ending id.

        Returns:
        The TrackPoint's list (ordered by id).
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                SELECT *
                FROM trackpoints
                WHERE _id >= ? and _id <= ?
                ORDER BY _id ASC
                """
                trackpoints = conn.execute(query, (trackpoint_from_id, trackpoint_to_id)).fetchall()
                if trackpoints:
                    return [TrackPoint(*tp) for tp in trackpoints]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

    def get_segments(self):
        """Get all segments.

        Return:
        list of Segment object sorted by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM segments ORDER BY _id"
                return [
                    Segment(*segment_tuple) for segment_tuple in conn.execute(query).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
        return []

    def get_segment_points(self, segmentid):
        """Get all segmentpoints from segment identify by segmentid.

        Return:
        list of SegmentPoint object sorted by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"SELECT * FROM segmentpoints WHERE segmentid={segmentid} ORDER BY _id"
                return [
                    SegmentPoint(*segmentpoint_tuple) for segmentpoint_tuple in conn.execute(query).fetchall()
                ]
            except Exception as error:
                # TODO add this error message to a logger system
                print(f"Error: [SQL] Couldn't execute the query: {error}")
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

    def bulk_insert(self, model_list, fk_value):
        """Bulk insertion for a model list.

        This method insert a list of models in an only transaction.

        Arguments:
        model_list -- a list of a model.
        fk_value   -- the value of the foreign key for the model.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                rowsInserted = 0
                for model in model_list:
                    cursor.execute(model.insert_query, model.bulk_insert_fields(fk_value))
                    rowsInserted = rowsInserted + 1
                conn.commit()
                return rowsInserted
            except Exception as error:
                # TODO add this error message to a logger system
                error_msg = f"Error: [SQL] Couldn't execute the query: {error}"
                print(error_msg)
        return 0

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

    def update_altitude(self, trackid, data_list):
        """Update all trackpoints altitude from trackid.

        trackid   - track's id where trackpoints has to belong to.
        data_list - list of data to update. Every item in the list has three keys: "latitude", "longitude", "elevation".
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                for data in data_list:
                    sql = """
                        update trackpoints
                        set altitude=?
                        where trackid=? and latitude=? and longitude=?
                    """
                    cursor.execute(sql, (data["elevation"], trackid, data["latitude"], data["longitude"]))
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
