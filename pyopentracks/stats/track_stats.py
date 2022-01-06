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

from parser import ParserError

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.utils.utils import LocationUtils


class TrackStats:

    class SensorNormalization:
        def __init__(self):
            self._max = None
            self._prev = None
            self._prev_time_ms = None
            self._total_time_s = 0
            self._total = 0

        def add(self, value: str, time_ms: float):
            if value is None:
                self.reset()
                return
            value = float(value)

            self._max = self._compute_max(value)

            if self._prev_time_ms is None:
                self._prev_time_ms = time_ms
                self._prev = value
                return

            elapsed_time_s = (time_ms - self._prev_time_ms) / 1000
            self._total_time_s = self._total_time_s + elapsed_time_s
            self._total = self._total + (value * elapsed_time_s)

            self._prev_time_ms = time_ms

        def reset(self):
            self._prev_time_ms = None

        @property
        def avg(self):
            if self._total == 0 and self._total_time_s == 0:
                return None
            return round(self._total / self._total_time_s)

        @property
        def max(self):
            if self._max:
                return round(self._max)
            return None

        def _compute_max(self, new_value):
            if new_value is None:
                return self._max
            if self._max is None:
                return new_value
            if new_value > self._max:
                return new_value
            else:
                return self._max

    def __init__(self):
        self._segment = None

        self._start_time_ms = None
        self._end_time_ms = None
        self._total_time_ms = None
        self._moving_time_ms = None
        self._last_segment_time_ms = None

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

        self._hr = TrackStats.SensorNormalization()
        self._cadence = TrackStats.SensorNormalization()

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
    def max_hr(self):
        return self._hr.max

    @property
    def avg_hr(self):
        return self._hr.avg

    @property
    def max_cadence(self):
        return self._cadence.max

    @property
    def avg_cadence(self):
        return self._cadence.avg

    def compute(self, track_points):
        """Compute stats from track_points

        It expects all track points are valid ones: correct location (lat, lon), time and speed.

        Arguments:
        track_points -- all TrackPoint's objects to compute that will be use to compute stats.
        """
        for tp in track_points:
            self._new_track_point(tp)

    def _new_track_point(self, track_point):
        """Compute all stats from new track point.

        It expects track_point to have the following data: latitude, longitude, time, speed.

        Arguments:
        track_point -- TrackPoint object with, at least, location (with latitude and longitude), time and speed.
        """
        if track_point.segment != self._segment:
            self._last_segment_time_ms = None
            self._hr.reset()
            self._cadence.reset()
        else:
            self._add_speed(self._get_float_or_none(track_point.speed))
            self._add_elevation(
                self._get_float_or_none(track_point.altitude),
                self._get_float_or_none(track_point.elevation_gain),
                self._get_float_or_none(track_point.elevation_loss)
            )
            self._add_distance(track_point.latitude, track_point.longitude)
            self._add_time(track_point.time_ms)
            self._hr.add(track_point.heart_rate, track_point.time_ms)
            self._cadence.add(track_point.cadence, track_point.time_ms)

        self._segment = track_point.segment
        self._last_latitude = track_point.latitude
        self._last_longitude = track_point.longitude

    def _get_float_or_none(self, data):
        return None if not data else float(data)

    def _add_time(self, timestamp_ms):
        """Add the time to the stats.

        Arguments:
        timestamp_ms -- time in millis.
        """
        try:
            if self._end_time_ms is not None:
                self._total_time_ms = (
                    self._total_time_ms + (timestamp_ms - self._end_time_ms)
                    if self._total_time_ms is not None
                    else timestamp_ms - self._end_time_ms
                )

            if self._last_segment_time_ms is not None:
                self._moving_time_ms = (
                    self._moving_time_ms + (timestamp_ms - self._last_segment_time_ms)
                    if self._moving_time_ms is not None
                    else timestamp_ms - self._last_segment_time_ms
                )

            self._start_time_ms = (
                timestamp_ms if self._start_time_ms is None
                else self._start_time_ms
            )
            self._end_time_ms = timestamp_ms
            self._last_segment_time_ms = timestamp_ms

        except ParserError as e:
            pyot_logging.get_logger(__name__).exception(f"datetime parsing error: {str(e)}")

    def _add_distance(self, lat, lon):
        if self._total_distance_m is None:
            self._total_distance_m = 0
        else:
            to_accum = LocationUtils.distance_between(self._last_latitude, self._last_longitude, lat, lon)
            self._total_distance_m = (self._total_distance_m + to_accum)

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
