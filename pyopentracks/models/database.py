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

import sqlite3
from os import path
from typing import List

from pyopentracks.models.section import Section

from pyopentracks.models.segment_track_record import SegmentTrackRecord
from pyopentracks.models.set import Set
from pyopentracks.utils import logging as pyot_logging
from pyopentracks.settings import xdg_data_home
from pyopentracks.models.activity import Activity
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.models.auto_import import AutoImport
from pyopentracks.models.aggregated_stats import AggregatedStats
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.models.segment import Segment
from pyopentracks.models.segment_point import SegmentPoint


config = {
    "database": path.join(xdg_data_home(), "database.db")
}


class Database:
    """SQLite database handler."""

    @property
    def _db_file(self) -> str:
        return config["database"]

    # @property
    # def _db_file(self) -> str:
    #     return path.join(self._db_dir, "database.db")

    # @property
    # def _db_dir(self) -> str:
    #     return xdg_data_home()

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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}: {query}"
                )

    def get_activity_by_id(self, _id):
        """Return Activity object from _id.

        Arguments:
        _id -- id of the activity to look up in the database.

        Return:
        Activity object or None if there is any Activity identified by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT activities.*, stats.* FROM activities, stats WHERE activities._id=? AND stats._id=activities.statsid"
                tuple_result = conn.execute(query, (_id,)).fetchone()
                if tuple_result:
                    return Activity(*tuple_result)
            except Exception as error:
                # TODO add this error message to a logger system
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return None

    def get_activities_between(self, begin, end):
        """Returns all activities between begin date and end date.

        Arguments:
        begin -- begin's date in milliseconds.
        end   -- end's date in milliseconds.

        Returns:
        List of activities between begin and end.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM activities WHERE starttime>=? AND starttime<=?"
                return [Activity(*t) for t in conn.execute(query, (begin, end)).fetchall()]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_segment_by_id(self, _id):
        """Return Segment object from _id.

        Arguments:
        _id -- id of the segment to look up in the database.

        Return:
        Segment object or None if there is any Activity identified by _id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM segments WHERE _id=?"
                tuple_result = conn.execute(query, (_id,)).fetchone()
                if tuple_result:
                    return Segment(*tuple_result)
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return None

    def get_segment_activities_by_activity_id(self, activity_id):
        """Return segmentracks from activity's id."""
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                    SELECT * 
                    FROM segmentracks 
                    WHERE activityid=?
                    ORDER BY _id
                """
                return [
                    SegmentTrack(*st) for st in conn.execute(query, (activity_id,)).fetchall()
                ]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_segment_tracks_by_segment_id(self, segment_id):
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
                    SegmentTrack(*st) for st in conn.execute(query, (segment_id,)).fetchall()
                ]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_segment_track_record(self, segment_id, time, year=None):
        """It gets the ranking for the segment's id according to the time.

        Arguments:
        segmentid -- segment's id.
        time -- time of the segment track to analyze.
        year -- (optional) filter by year if any.

        Returns:
        A SegmentTrackRecord object.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                optional_where = "" if year is None else f"AND strftime('%Y', t.starttime / 1000, 'unixepoch')='{year}'"
                query = f"""
                    SELECT st._id segmenttrackid, COUNT(*) + 1 ranking, MIN(st.time) best_time 
                    FROM segmentracks st, activities t
                    WHERE st.segmentid=? AND st.activityid=t._id AND st.time<? {optional_where}   
                    GROUP BY st.segmentid                        
                    ORDER BY time ASC
                """
                tuple_result = conn.execute(query, (segment_id, time)).fetchone()
                if tuple_result:
                    return SegmentTrackRecord(*tuple_result)
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return None

    def get_activities(self):
        """Get all activities from database.

        Return:
            list of Activity object sorted by start time.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM activities ORDER BY starttime DESC"
                return [
                    Activity(*activity) for activity in conn.execute(query).fetchall()
                ]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_points_near_point_start(self, bbox, activity_id=None):
        """Look for points inside trackpoints table that are inside the bounding box bbox.

        Arguments:
        bbox    -- the BoundingBox's object (north, east, south and west Locations).
        activity_id -- (optional) activity's id where looking for points.

        Returns:
        list of SegmentTrack.Point with all points inside p1, p2, p3 and p4 bounding box.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                where = f" sections.activityid = {activity_id} AND " if activity_id else ""
                query = f"""
                    SELECT
                        sections.activityid,
                        trackpoints._id,
                        trackpoints.time,
                        trackpoints.latitude,
                        trackpoints.longitude
                    FROM
                        sections, trackpoints
                    WHERE
                        {where}
                        sections._id=trackpoints.sectionid AND
                        trackpoints.latitude > {bbox.south.latitude} AND
                        trackpoints.latitude < {bbox.north.latitude} AND
                        trackpoints.longitude < {bbox.east.longitude} AND
                        trackpoints.longitude > {bbox.west.longitude}
                    ORDER BY sections.activityid DESC, trackpoints.time ASC
                """
                return [
                    SegmentTrack.Point(*row) for row in conn.execute(query).fetchall()
                ]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_points_near_point_end(self, bbox, activity_id, trackpoint_id_from):
        """Look for points inside activities identify by activity_id that are inside the bounding box bbox.

        Only trackpoints identify by an id greater than trackpoint_id_from.

        Arguments:
        bbox               -- the BoundingBox's object (north, east, south and west Locations).
        activity_id        -- activity id where it'll look for points inside p1, p2, p3 and p4.
        trackpoint_id_from -- trackpoints id from it'll look for points inside p1, p2, p3 and p4.

        Returns:
        The recorded SegmentTrack.Point sooner inside p1, p2, p3 and p4.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"""
                    SELECT
                        sections.activityid,
                        trackpoints._id,
                        trackpoints.time,
                        trackpoints.latitude,
                        trackpoints.longitude,
                        MIN(trackpoints.time)
                    FROM
                        sections, trackpoints
                    WHERE
                        sections._id=trackpoints.sectionid AND
                        sections.activityid = {activity_id} AND
                        trackpoints._id > {trackpoint_id_from} AND
                        trackpoints.latitude > {bbox.south.latitude} AND
                        trackpoints.latitude < {bbox.north.latitude} AND
                        trackpoints.longitude < {bbox.east.longitude} AND
                        trackpoints.longitude > {bbox.west.longitude}
                    GROUP BY trackpoints.time
                    ORDER BY trackpoints.time ASC
                """
                tuple_result = conn.execute(query).fetchone()
                return SegmentTrack.Point(*tuple_result) if tuple_result else None
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_existed_activities(self, uuid, start, end):
        """Look for a Activity from arguments.

        Look for an activity that has the same uuid or has the same start and
        end time.

        Arguments:
        uuid -- UUID that could be None.
        start -- start time in milliseconds.
        end -- end time in milliseconds.

        Return:
        list of activities or None.

        Raise:
        raise the exception could be triggered.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = """
                SELECT activities.*, stats.* FROM activities, stats
                WHERE stats._id=activities.statsid AND (activities.uuid=? OR (activities.starttime=? and stats.stoptime=?))
                """
                tuple_result = conn.execute(query, (uuid, start, end)).fetchall()
                if tuple_result:
                    return [Activity(*tuple) for tuple in tuple_result]
                return None
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                     AND stats.starttime>={date_from} and stats.starttime<={date_to}
                    """
                elif date_from:
                    where = f" AND stats.starttime>={date_from}"
                elif date_to:
                    where = f" AND stats.starttime<={date_to}"
                else:
                    where = ""

                query = f"""
                SELECT
                    category,
                    COUNT(*) total_activities,
                    SUM(stats.totaltime) total_time,
                    SUM(stats.movingtime) total_moving_time,
                    SUM(stats.totaldistance) total_distance,
                    SUM(stats.elevationgain) total_gain,
                    AVG(stats.totaltime) avg_time,
                    AVG(stats.movingtime) avg_moving_time,
                    AVG(stats.totaldistance) avg_distance,
                    AVG(stats.elevationgain) avg_gain,
                    SUM(stats.totaldistance) / (SUM(stats.movingtime) / 1000) avg_speed,
                    AVG(stats.avghr) avg_heart_rate,
                    AVG(stats.avgcadence) avg_cadence,
                    MAX(stats.totaltime) max_time,
                    MAX(stats.movingtime) max_moving_time,
                    MAX(stats.totaldistance) max_distance,
                    MAX(stats.elevationgain) max_gain,
                    MAX(stats.maxspeed) max_speed,
                    MAX(stats.maxhr) max_heart_rate,
                    MAX(stats.maxcadence) max_cadence
                FROM stats, activities
                WHERE stats._id=activities.statsid
                {where}
                GROUP BY category
                ORDER BY {order_by} DESC;
                """

                stats = conn.execute(query).fetchall()
                if stats:
                    return [AggregatedStats(*s) for s in stats]
                return None
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                FROM activities
                ORDER BY starttime DESC
                """
                items = conn.execute(query).fetchall()
                if items:
                    return [i[0] for i in items]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_sections(self, activity_id):
        """Get all sections with its track points from activity identified by activity_id.

        Arguments:
        activity_id -- Activity's id.

        Return:
        list of all sections.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"SELECT * FROM sections WHERE sections.activityid=? ORDER BY _id ASC"
                list_result = conn.execute(query, (activity_id,)).fetchall()
                if not list_result:
                    return []

                sections_to_return = []                
                for result in list_result:
                    section = Section(*result)
                    section.track_points.extend(self.get_section_track_points(section.id))
                    sections_to_return.append(section)

                return sections_to_return
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_sets(self, stats_id):
        """Get all sets from stats identified by stats_id.

        Arguments:
        stats_id -- Stats's id.

        Return:
        list of all sets.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"SELECT * FROM sets WHERE sets.statsid=? ORDER BY _id ASC"
                list_result = conn.execute(query, (stats_id,)).fetchall()
                return [Set(*result) for result in list_result]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_section_track_points(self, sectionid):
        """Get all section track points identified by sectionid."""
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = f"SELECT * FROM trackpoints WHERE sectionid=? ORDER BY _id ASC"
                trackpoints = conn.execute(query, (sectionid,)).fetchall()
                if trackpoints:
                    return [TrackPoint(*tp) for tp in trackpoints]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def get_track_points(self, activity_id, from_trackpoint_id=None, to_trackpoint_id=None):
        """Get all track points from track identified by trackid.

        Arguments:
        activity_id -- Activity's id.
        from_trackpoint_id -- initial track point.
        to_trackpoint_Id -- end track point.

        Return:
        list of all TrackPoint objects that hast the Activity identified
        by activity_id.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                extra_where = ""
                if from_trackpoint_id is not None:
                    extra_where += f" AND _id >= {from_trackpoint_id} "
                if to_trackpoint_id is not None:
                    extra_where += f" AND _id <= {to_trackpoint_id} "
                query = f"SELECT * FROM trackpoints WHERE sectionid in (select _id from sections where activityid=? ORDER BY _id ASC) {extra_where} ORDER BY _id ASC"
                trackpoints = conn.execute(query, (activity_id,)).fetchall()
                if trackpoints:
                    return [TrackPoint(*tp) for tp in trackpoints]
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return []

    def insert_track_activity(self, activity: Activity):
        """Inserts a track activity.
        
        It inserts the stats, sections and track_points if they are into the
        track's object.

        Return
            the id of the track's activity inserted or None if any error.
        """
        if activity is None:
            pyot_logging.get_logger(__name__).debug("The activity to be inserted is None")
            return None

        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()

                statsid = None
                if activity.stats:
                    activity.stats_id = statsid
                    cursor.execute(activity.stats.insert_query, activity.stats.fields)
                    statsid = cursor.lastrowid

                activity_id = None
                if statsid is not None:
                    activity.stats_id = statsid
                    cursor.execute(activity.insert_query, activity.fields)
                    activity_id = cursor.lastrowid

                if activity_id is not None and activity.sections:
                    for section in activity.sections:
                        section.activity_id = activity_id
                        cursor.execute(section.insert_query, section.fields)
                        sectionid = cursor.lastrowid
                        if sectionid is not None:
                            for track_point in section.track_points:
                                cursor.execute(track_point.insert_query, track_point.bulk_insert_fields(sectionid))

                conn.commit()

                return activity_id
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
                conn.rollback()
                return None

    def insert_set_activity(self, activity: Activity, sets: List[Set]):
        """Inserts a set activity.
        
        It inserts the stats and sets also.

        Return
            the id of the set's activity inserted or None if any error.
        """
        if activity is None:
            pyot_logging.get_logger(__name__).debug("The activity to be inserted is None")
            return None

        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()

                statsid = None
                if activity.stats:
                    activity.stats_id = statsid
                    cursor.execute(activity.stats.insert_query, activity.stats.fields)
                    statsid = cursor.lastrowid

                activity_id = None
                if statsid is not None:
                    activity.stats_id = statsid
                    cursor.execute(activity.insert_query, activity.fields)
                    activity_id = cursor.lastrowid

                    for set in sets:
                        set.stats_id = statsid
                        cursor.execute(set.insert_query, set.fields)

                conn.commit()

                return activity_id
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
                conn.rollback()
                return None

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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query {model.insert_query}: {error}"
                )
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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )

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
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )

    def update_altitude(self, activity_id, data_list):
        """Update all trackpoints altitude from activity_id.

        activity_id   - activity's id where trackpoints has to belong to.
        data_list - list of data to update. Every item in the list has three keys: "latitude", "longitude", "elevation".
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                cursor = conn.cursor()
                for data in data_list:
                    sql = """
                        update trackpoints
                        set altitude=?
                        where activity_id=? and latitude=? and longitude=?
                    """
                    cursor.execute(sql, (data["elevation"], activity_id, data["latitude"], data["longitude"]))
                conn.commit()
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )

    def get_autoimport_by_activity_file(self, pathfile: str):
        """Return AutoImport object from activityfile.

        Arguments:
        pathfile -- the path of the file.

        Return:
        AutoImport object or None if there is any AutoImport with path.
        """
        with sqlite3.connect(self._db_file) as conn:
            try:
                query = "SELECT * FROM autoimport WHERE activityfile=?"
                tuple_result = conn.execute(query, (pathfile,)).fetchone()
                if tuple_result:
                    return AutoImport(*tuple_result)
            except Exception as error:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: [SQL] Couldn't execute the query: {error}"
                )
        return None
