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

from pyopentracks.utils.utils import TimeUtils as tu


class TrackStats:
    # Speed threshold for considering that there is not movement (in mps).
    # TODO This should be a setting's option ¿?
    AUTO_PAUSE_SPEED_THRESHOLD = 0.1

    class SensorNormalization:
        def __init__(self):
            self._max_hr = None
            self._prev_hr = None
            self._prev_time_ms = None
            self._total_time_s = 0
            self._total_hr = 0

        def add_hr(self, hr_bpm: str, time_ms: float):
            if hr_bpm is None:
                self.reset()
                return
            hr_bpm = float(hr_bpm)

            self._max_hr = self._compute_max_hr(hr_bpm)

            if self._prev_time_ms is None:
                self._prev_time_ms = time_ms
                self._prev_hr = hr_bpm
                return

            elapsed_time_s = (time_ms - self._prev_time_ms) / 1000
            self._total_time_s = self._total_time_s + elapsed_time_s
            self._total_hr = self._total_hr + (hr_bpm * elapsed_time_s)

            self._prev_time_ms = time_ms

        def reset(self):
            self._prev_time_ms = None

        @property
        def avg_hr(self):
            if self._total_hr == 0 and self._total_time_s == 0:
                return None
            return round(self._total_hr / self._total_time_s)

        @property
        def max_hr(self):
            if self._max_hr:
                return round(self._max_hr)
            return None

        def _compute_max_hr(self, new_hr):
            if new_hr is None:
                return self._max_hr
            if self._max_hr is None:
                return new_hr
            if new_hr > self._max_hr:
                return new_hr
            else:
                return self._max_hr

    def __init__(self):
        self._sensor = TrackStats.SensorNormalization()

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

        self._max_hr = None
        self._avg_hr = None

        self._track_points = []

    @property
    def start_time(self):
        return self._start_time_ms

    @property
    def end_time(self):
        return self._end_time_ms

    @property
    def total_time(self):
        return self._total_time_ms

    @property
    def moving_time(self):
        return self._moving_time_ms

    @property
    def total_distance(self):
        return self._total_distance_m

    @property
    def avg_speed(self):
        return self._avg_speed_mps

    @property
    def max_speed(self):
        return self._max_speed_mps

    @property
    def avg_moving_speed(self):
        return self._avg_moving_speed_mps

    @property
    def max_elevation(self):
        return self._max_elevation_m

    @property
    def min_elevation(self):
        return self._min_elevation_m

    @property
    def gain_elevation(self):
        return self._gain_elevation_m

    @property
    def loss_elevation(self):
        return self._loss_elevation_m

    @property
    def track_points(self):
        return self._track_points

    @property
    def max_hr(self):
        return self._sensor.max_hr

    @property
    def avg_hr(self):
        return self._sensor.avg_hr

    def new_track_point(self, track_point, num_segment):
        """Compute all stats from new track point.

        Arguments:
        track_point -- TrackPoint object with, at least, location
                       (with latitude and longitude) and time.
        num_segment -- a GPX file consiste in a number of segments.
                       This argument contains the number of segment the
                       track point belongs.
        """
        if not track_point:
            return
        if not track_point.location or not track_point.time:
            return
        if not self._is_valid_location(track_point.location):
            return

        self._end_segment_time_ms = (
            self._end_segment_time_ms if num_segment == self._segment else None
        )
        self._segment = num_segment

        self._add_track_point(track_point)
        self._add_distance(track_point.location)
        self._add_speed(self._get_float_or_none(track_point.speed))
        self._add_elevation(
            self._get_float_or_none(track_point.elevation),
            self._get_float_or_none(track_point.elevation_gain),
            self._get_float_or_none(track_point.elevation_loss)
        )

        if not self._is_moving(track_point.speed):
            self._end_segment_time_ms = None
            self._sensor.reset()
        else:
            self._add_time(track_point.time)
            self._sensor.add_hr(
                track_point.heart_rate,
                tu.iso_to_ms(track_point.time)
            )

    def _is_moving(self, speed):
        return speed and float(speed) >= TrackStats.AUTO_PAUSE_SPEED_THRESHOLD

    def _get_float_or_none(self, data):
        return None if not data else float(data)

    def _add_track_point(self, track_point):
        self._track_points.append(track_point)

    def _add_time(self, time):
        """Add the time to the stats.

        Arguments:
        time -- a string representing the time in ISO 8601 format.
        """
        try:
            timestamp_ms = tu.iso_to_ms(time)

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
