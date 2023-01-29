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

from pyopentracks.models.database import Database
from pyopentracks.models.segment import Segment
from pyopentracks.models.segment_point import SegmentPoint
from pyopentracks.tasks.segment_search import SegmentSearch, SegmentTrackSearch
from pyopentracks.utils.utils import DateTimeUtils


class DatabaseHelper:

    @staticmethod
    def get_activity_by_id(id):
        db = Database()
        return db.get_activity_by_id(id)

    @staticmethod
    def get_activities():
        db = Database()
        return db.get_activities()

    @staticmethod
    def get_existed_activities(activity):
        db = Database()
        return db.get_existed_activities(activity.uuid, activity.start_time_ms, activity.stats.end_time_ms)

    @staticmethod
    def get_subactivities(id):
        db = Database()
        return db.get_subactivities(id)

    @staticmethod
    def get_sections(activity_id):
        db = Database()
        return db.get_sections(activity_id)

    @staticmethod
    def get_sets(stats_id):
        db = Database()
        return db.get_sets(stats_id)

    @staticmethod
    def get_track_points(activity_id, from_trackpoint_id=None, to_trackpoint_id=None):
        db = Database()
        return db.get_track_points(activity_id, from_trackpoint_id, to_trackpoint_id)

    @staticmethod
    def get_aggregated_stats(date_from=None, date_to=None, order_by_categories=False):
        db = Database()
        return db.get_aggregated_stats(date_from, date_to, order_by="category" if order_by_categories else "total_activities")

    @staticmethod
    def get_years():
        db = Database()
        return db.get_years()

    @staticmethod
    def create_segment(name: str, distance: float, gain: int, loss: int, points: list):
        """Creates a segment.

        Arguments:
        name     -- segment's name.
        distance -- segment's distance.
        gain     -- segment's elevation gain.
        loss     -- segment's elevation loss.
        points   -- segment's TrackPoint list

        Return:
        Segment's object and the list of SegmentPoint's object.
        """
        db = Database()
        segment = Segment(None, name, distance, gain, loss)
        segment.id = db.insert(segment)
        segment_points = [ SegmentPoint(None, segment.id, tp.latitude, tp.longitude, tp.altitude) for tp in points ]
        db.bulk_insert(segment_points, segment.id)
        segment_search = SegmentSearch(segment, segment_points)
        segment_search.start()

    @staticmethod
    def insert_track_activity(activity):
        """Inserts a track activity and all its data (stats, sections, points...)"""
        db = Database()
        activity_id = db.insert_track_activity(activity)
        if activity_id is not None:
            segment_track_search = SegmentTrackSearch(activity_id)
            segment_track_search.start()
        return activity_id

    @staticmethod
    def insert_set_activity(activity, sets):
        """Inserts a set activity and all its data"""
        db = Database()
        activity_id = db.insert_set_activity(activity, sets)
        return activity_id

    @staticmethod
    def insert_multi_activity(multi_activity):
        """Inserts a the multi activity and all their activities"""
        db = Database()
        multi_activity_id = db.insert_multi_activity(multi_activity)
        return multi_activity_id

    @staticmethod
    def bulk_insert(list_to_insert, fk):
        """Insert the list of models and return the number of items inserted."""
        db = Database()
        return db.bulk_insert(list_to_insert, fk)

    @staticmethod
    def get_segments():
        db = Database()
        return db.get_segments()

    @staticmethod
    def get_segment_by_id(id):
        db = Database()
        return db.get_segment_by_id(id)

    @staticmethod
    def get_segment_tracks_by_activity_id(activity_id):
        db = Database()
        return db.get_segment_activities_by_activity_id(activity_id)

    @staticmethod
    def get_segment_tracks_by_segment_id(segment_id, fetch_track=False):
        db = Database()
        segment_tracks = db.get_segment_tracks_by_segment_id(segment_id)
        if not fetch_track:
            return segment_tracks

        for st in segment_tracks:
            st.activity = DatabaseHelper.get_activity_by_id(st.activity_id)

        return segment_tracks

    @staticmethod
    def get_segment_tracks():
        """Gets and returns all segmentracks ordered by segmentid.

        Return:
        A list with all segments with segmentracks, like this:
        [
            {
                segment: <segment's object>,
                segmentracks: [<object 1>, ..., <object n>]
            },
            ...

            {
                segment: <segment's object>,
                segmentracks: [<object 1>, ..., <object n>]
            },
        ]
        """
        result_list = []
        db = Database()
        for segment in db.get_segments():
            obj = {
                "segment": segment,
                "segmentracks": []
            }
            for segmentracks in db.get_segment_tracks_by_segment_id(segment.id):
                obj["segmentracks"].append(segmentracks)
            result_list.append(obj)

        return result_list

    @staticmethod
    def get_segment_points(segmentid):
        db = Database()
        return db.get_segment_points(segmentid)

    @staticmethod
    def update_altitude(activity_id, results):
        """Update altitude for trackpoints that belong to the activity identified by activity_id with results dictionary.

        Arguments:
        activity_id - activity's id.
        results - list of dictionaries with keys: "latitude", "longitude" and "elevation".
        """
        db = Database()
        db.update_altitude(activity_id, results)

    @staticmethod
    def update_stats(activity_id, gain, loss, min_elevation=None, max_elevation=None):
        db = Database()
        activity = db.get_activity_by_id(activity_id)
        activity.gain_elevation_m = gain
        activity.loss_elevation_m = loss
        if max_elevation is not None:
            activity.max_elevation_m = max_elevation
        if min_elevation is not None:
            activity.min_elevation_m = min_elevation
        db.update(activity)

    @staticmethod
    def update(model):
        db = Database()
        db.update(model)

    @staticmethod
    def delete(model):
        db = Database()
        db.delete(model)

    @staticmethod
    def get_activities_in_day(y: int, m: int, d: int):
        db = Database()
        return db.get_activities_between(DateTimeUtils.begin_of_day(y, m, d), DateTimeUtils.end_of_day(y, m, d))

    @staticmethod
    def get_segment_track_record(segmentid, time, year=None):
        db = Database()
        return db.get_segment_track_record(segmentid, time, year)
