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

from datetime import datetime
from parser import ParserError
from math import radians, sin, cos, asin, sqrt

from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import DistanceUtils as du
from pyopentracks.utils.utils import SpeedUtils as su
from pyopentracks.utils.utils import ElevationUtils as eu


class Track:
    def __init__(self):
        self._name = None
        self._desc = None
        self._type = None
        self._track_stats = None

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._desc

    @property
    def activity_type(self):
        return self._type

    @property
    def track_stats(self):
        return self._track_stats


class TrackStats:
    # Speed threshold for considering that there is not movement (in mps).
    # TODO This should be a setting's option ¿?
    AUTO_PAUSE_SPEED_THRESHOLD = 0.1

    def __init__(self):
        self._segment = None

        self._start_time_ms = None
        self._end_time_ms = None
        self._total_time_ms = None
        self._moving_time_ms = None
        self._end_segment_time_ms = None

        self._last_latitude = None
        self._last_longitude = None
        self._total_distance_m = None

        self._avg_speed_mps = None
        self._max_speed_mps = None
        self._avg_moving_speed_mps = None

        self._max_elevation_m = None
        self._min_elevation_m = None
        self._gain_elevation_m = None
        self._loss_elevation_m = None

        self._locations = []

    @property
    def start_time(self):
        return dtu.ms_to_str(self._start_time_ms)

    @property
    def end_time(self):
        return dtu.ms_to_str(self._end_time_ms)

    @property
    def total_time(self):
        return tu.ms_to_str(self._total_time_ms)

    @property
    def moving_time(self):
        return tu.ms_to_str(self._moving_time_ms)

    @property
    def total_distance(self):
        return du.m_to_str(self._total_distance_m)

    @property
    def avg_speed(self):
        return su.mps_to_kph(self._avg_speed_mps)

    @property
    def max_speed(self):
        return su.mps_to_kph(self._max_speed_mps)

    @property
    def avg_moving_speed(self):
        return su.mps_to_kph(self._avg_moving_speed_mps)

    @property
    def max_elevation(self):
        return eu.elevation_to_str(self._max_elevation_m)

    @property
    def min_elevation(self):
        return eu.elevation_to_str(self._min_elevation_m)

    @property
    def gain_elevation(self):
        return eu.elevation_to_str(self._gain_elevation_m)

    @property
    def loss_elevation(self):
        return eu.elevation_to_str(self._loss_elevation_m)

    def new_track_point(self, track_point, num_segment):
        """Compute all stats from new track point.

        Arguments:
        track_point -- data in a dictionary with, at least, location
                       (with latitude and longitude) and time.
        num_segment -- a GPX file consiste in a number of segments.
                       This argument contains the number of segment the
                       track point belongs.
        """
        if not isinstance(track_point, dict):
            return
        if "location" not in track_point or "time" not in track_point:
            return
        if not self._is_valid_location(track_point["location"]):
            return

        self._end_segment_time_ms = (
            self._end_segment_time_ms if num_segment == self._segment else None
        )
        self._segment = num_segment

        self._add_location(track_point["location"])
        self._add_distance(track_point["location"])
        self._add_speed(self._get_float_or_none("speed", track_point))
        self._add_elevation(
            self._get_float_or_none("elevation", track_point),
            self._get_float_or_none("elevation_gain", track_point),
            self._get_float_or_none("elevation_loss", track_point)
        )
        if float(track_point["speed"]) < TrackStats.AUTO_PAUSE_SPEED_THRESHOLD:
            self._end_segment_time_ms = None
        else:
            self._add_time(track_point["time"])

    def _get_float_or_none(self, idx, dictionary):
        if idx in dictionary and dictionary[idx] is not None:
            return float(dictionary[idx])
        return None

    def _add_location(self, location):
        self._locations.append(
            (float(location["latitude"]), float(location["longitude"]))
        )

    def _add_time(self, time):
        """Add the time to the stats.

        Arguments:
        time -- a string representing the time in ISO 8601 format.
        """
        try:
            timestamp_ms = datetime.fromisoformat(
                time.replace("Z", "+00:00")
            ).timestamp() * 1000

            if self._end_time_ms is not None:
                self._total_time_ms = (
                    self._total_time_ms + (timestamp_ms - self._end_time_ms)
                    if self._total_time_ms is not None
                    else timestamp_ms - self._end_time_ms
                )

            if self._end_segment_time_ms is not None:
                self._moving_time_ms = (
                    self._moving_time_ms + (timestamp_ms - self._end_segment_time_ms)
                    if self._moving_time_ms is not None
                    else timestamp_ms - self._end_segment_time_ms
                )

            self._start_time_ms = (
                timestamp_ms if self._start_time_ms is None
                else self._start_time_ms
            )
            self._end_time_ms = timestamp_ms
            self._end_segment_time_ms = timestamp_ms

        except ParserError as e:
            print("Date time parsing Error", e)

    def _add_distance(self, location):
        if self._total_distance_m is None:
            self._total_distance_m = 0
        else:
            to_accum = self._distance_to(
                float(self._last_latitude),
                float(self._last_longitude),
                float(location["latitude"]),
                float(location["longitude"])
            )
            self._total_distance_m = (self._total_distance_m + to_accum)
        self._last_latitude = location["latitude"]
        self._last_longitude = location["longitude"]

    def _add_speed(self, speed):
        if speed is not None:
            self._max_speed_mps = (
                speed
                if self._max_speed_mps is None or speed > self._max_speed_mps
                else self._max_speed_mps
            )
        if self._total_distance_m and self._total_time_ms:
            self._avg_speed_mps = (
                self._total_distance_m / (self._total_time_ms / 1000)
            )
        if self._total_distance_m and self._moving_time_ms:
            self._avg_moving_speed_mps = (
                self._total_distance_m / (self._moving_time_ms / 1000)
            )

    def _add_elevation(self, ele, gain, loss):
        if ele is not None:
            self._max_elevation_m = (
                ele
                if self._max_elevation_m is None or ele > self._max_elevation_m
                else self._max_elevation_m
            )
            self._min_elevation_m = (
                ele
                if self._min_elevation_m is None or ele < self._min_elevation_m
                else self._min_elevation_m
            )
        if gain is not None:
            self._gain_elevation_m = (
                self._gain_elevation_m + gain
                if self._gain_elevation_m is not None
                else gain
            )
        if loss is not None:
            self._loss_elevation_m = (
                self._loss_elevation_m + loss
                if self._loss_elevation_m is not None
                else loss
            )

    def _is_valid_location(self, location):
        try:
            if not isinstance(location, dict):
                return False
            if "latitude" not in location or "longitude" not in location:
                return False
            if not location["latitude"] or not location["longitude"]:
                return False
            if (not (abs(float(location["latitude"])) <= 90 and
                     abs(float(location["longitude"])) <= 180)):
                return False
        except Exception as e:
            print("Valid location exception:", e)
            return False
        return True

    def _distance_to(self, lat1, lon1, lat2, lon2):
        """Hervasian algorithm.

        Return:
        Distance between the two locations (lat1, lon1) to (lat2, lon2)
        in meters.
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * 6371 * asin(sqrt(a)) * 1000
