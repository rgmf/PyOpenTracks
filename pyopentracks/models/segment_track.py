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

from .model import Model
from pyopentracks.stats.track_activity_stats import TrackActivityStats
from pyopentracks.utils.utils import TimeUtils, SpeedUtils, SensorUtils


class SegmentTrack(Model):
    """
    A SegmentTrack is a segment with two points: from-point and to-point.
    """

    class Point:
        """
        Point (from-point or to-point) in a SegmentTrack.
        """
        def __init__(self, *args):
            self._activity_id = args[0] if args else None
            self._trackpoint_id = args[1] if args else None
            self._timestamp = args[2] if args else None
            self._latitude = args[3] if args else None
            self._longitude = args[4] if args else None

        @property
        def activity_id(self):
            return self._activity_id

        @property
        def trackpoint_id(self):
            return self._trackpoint_id

        @property
        def timestamp(self):
            return self._timestamp

        @property
        def latitude(self):
            return self._latitude

        @property
        def longitude(self):
            return self._longitude

    def __init__(self, *args):
        self._id = args[0] if args else None
        self._segmentid = args[1] if args else None
        self._activity_id = args[2] if args else None
        self._trackpoint_id_start = args[3] if args else None
        self._trackpoint_id_end = args[4] if args else None
        self._time = args[5] if args else None
        self._maxspeed = args[6] if args else None
        self._avgspeed = args[7] if args else None
        self._maxhr = args[8] if args else None
        self._avghr = args[9] if args else None
        self._maxcadence = args[10] if args else None
        self._avgcadence = args[11] if args else None
        self._avgpower = args[12] if args else None
        self._activity = None

    @staticmethod
    def from_points(segment_id: int, stats: TrackActivityStats, from_point: Point, to_point: Point):
        segment_track = SegmentTrack()
        segment_track._segmentid = segment_id
        segment_track._activity_id = from_point.activity_id
        segment_track._trackpoint_id_start = from_point.trackpoint_id
        segment_track._trackpoint_id_end = to_point.trackpoint_id
        segment_track._time = stats.total_time
        segment_track._maxspeed = stats.max_speed
        segment_track._avgspeed = stats.avg_speed
        segment_track._maxhr = stats.max_hr
        segment_track._avghr = stats.avg_hr
        segment_track._maxcadence = stats.max_cadence
        segment_track._avgcadence = stats.avg_cadence
        #segment_track._avgpower = stats.avg_power

        return segment_track

    @property
    def insert_query(self):
        """Returns the query for inserting a SegmentTrack register."""
        return "INSERT INTO segmentracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    @property
    def delete_query(self):
        """Returns the query for deleting a SegmentTrack by id."""
        return "DELETE FROM segmentracks WHERE _id=?"

    @property
    def update_query(self):
        return None

    @property
    def update_data(self):
        return None

    @property
    def fields(self):
        """Returns a tuple with all Segment fields.
        Maintain the database table segments order of the fields."""
        return (
            self._id,
            self._segmentid,
            self._activity_id,
            self._trackpoint_id_start,
            self._trackpoint_id_end,
            self._time,
            self._maxspeed,
            self._avgspeed,
            self._maxhr,
            self._avghr,
            self._maxcadence,
            self._avgcadence,
            self._avgpower
        )

    def bulk_insert_fields(self, fk_value):
        return None

    @property
    def id(self):
        return self._id

    @property
    def segmentid(self):
        return self._segmentid

    @property
    def activity_id(self):
        return self._activity_id

    @property
    def track_point_id_start(self):
        return self._trackpoint_id_start

    @property
    def track_point_id_end(self):
        return self._trackpoint_id_end

    @property
    def activity(self):
        return self._activity

    @property
    def time_ms(self):
        return self._time

    @property
    def time(self):
        return TimeUtils.ms_to_str(self._time)

    @property
    def maxspeed(self):
        if self.activity is not None:
            return SpeedUtils.mps_to_category_rate(self._maxspeed, self.activity.category)
        return SpeedUtils.mps_to_kph(self._maxspeed)

    @property
    def avgspeed(self):
        if self.activity is not None:
            return SpeedUtils.mps_to_category_rate(self._avgspeed, self.activity.category)
        return SpeedUtils.mps_to_kph(self._avgspeed)

    @property
    def avghr(self):
        return SensorUtils.hr_to_str(self._avghr)

    @property
    def maxhr(self):
        return SensorUtils.hr_to_str(self._maxhr)

    @property
    def avgcadence(self):
        return SensorUtils.cadence_to_str(self._avgcadence, self.activity.category)

    @property
    def maxcadence(self):
        return SensorUtils.cadence_to_str(self._maxcadence, self.activity.category)

    @activity.setter
    def activity(self, activity):
        self._activity = activity
