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
from abc import abstractmethod
from dateutil.parser import ParserError
from typing import List

from pyopentracks.models.section import Section
from pyopentracks.models.track_point import TrackPoint

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.utils.utils import (
    LocationUtils, TimeUtils, SensorUtils, ElevationUtils,
    DistanceUtils, SpeedUtils, TypeActivityUtils
)


class TrackActivityStats:

    def __init__(self):
        self._start_time_ms = None
        self._end_time_ms = None
        self._total_time_ms = None
        self._moving_time_ms = None
        self._last_section_time_ms = None

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

        self._hr = SensorNormalization()
        self._cadence = SensorNormalization()
        self._temperature = SensorNormalization()

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
    def moving_time_str(self):
        return TimeUtils.ms_to_str(self._moving_time_ms)

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
    def gain_elevation_str(self):
        return ElevationUtils.elevation_to_str(self._gain_elevation_m)

    @property
    def loss_elevation(self):
        return self._loss_elevation_m

    @property
    def loss_elevation_str(self):
        return ElevationUtils.elevation_to_str(self._loss_elevation_m)

    @property
    def max_hr(self):
        return self._hr.max

    @property
    def max_hr_str(self):
        return SensorUtils.hr_to_str(self._hr.max)

    @property
    def avg_hr(self):
        return self._hr.avg

    @property
    def avg_hr_str(self):
        return SensorUtils.hr_to_str(self._hr.avg)

    @property
    def max_cadence(self):
        return self._cadence.max

    @property
    def avg_cadence(self):
        return self._cadence.avg

    @property
    def min_temperature(self):
        return self._temperature.min

    @property
    def min_temperature_str(self):
        return SensorUtils.temperature_to_str(self._temperature.min)

    @property
    def max_temperature(self):
        return self._temperature.max

    @property
    def max_temperature_str(self):
        return SensorUtils.temperature_to_str(self._temperature.max)

    @property
    def avg_temperature(self):
        return self._temperature.avg

    @property
    def avg_temperature_str(self):
        return SensorUtils.temperature_to_str(self._temperature.avg)

    def compute(self, obj: any):
        if not isinstance(obj, list) or not obj:
            pyot_logging.get_logger(__name__).debug(
                "Cannot compute the object because is not a list or is an empty list"
            )
            return

        if isinstance(obj[0], Section):
            self._compute(obj)
        elif isinstance(obj[0], TrackPoint):
            section = Section()
            section.track_points.extend(obj)
            self._compute([section])
        else:
            pyot_logging.get_logger(__name__).error(
                "Error: TrackStats can only compute list of TrackPoint or list of Section, not " + str(type(obj))
            )

    def _compute(self, sections: List[Section]):
        """Compute stats from track_points

        It expects all track points inside each section are valid ones:
        correct location (lat, lon), time and speed.

        Arguments:
            sections -- all sections with the points.
        """
        for section in sections:
            self._new_section(section)

            self._last_section_time_ms = None
            self._hr.reset()
            self._cadence.reset()
            self._temperature.reset()

        self._avg_speed_mps = self._total_distance_m / (self._total_time_ms / 1000) if self._total_time_ms else 0
        self._avg_moving_speed_mps = self._total_distance_m / (self._moving_time_ms / 1000) if self._moving_time_ms else 0

    def _new_section(self, section: Section):
        for tp in section.track_points:
            self._new_track_point(tp)

    def _new_track_point(self, track_point: TrackPoint):
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
        self._temperature.add(track_point.temperature, track_point.time_ms)

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

            if self._last_section_time_ms is not None:
                self._moving_time_ms = (
                    self._moving_time_ms + (timestamp_ms - self._last_section_time_ms)
                    if self._moving_time_ms is not None
                    else timestamp_ms - self._last_section_time_ms
                )

            self._start_time_ms = (
                timestamp_ms if self._start_time_ms is None
                else self._start_time_ms
            )
            self._end_time_ms = timestamp_ms
            self._last_section_time_ms = timestamp_ms

        except ParserError as e:
            pyot_logging.get_logger(__name__).exception(
                f"datetime parsing error: {str(e)}"
            )

    def _add_distance(self, lat, lon):
        if self._total_distance_m is None:
            self._total_distance_m = 0
        else:
            to_accum = LocationUtils.distance_between(
                self._last_latitude, self._last_longitude,
                lat, lon
            )
            self._total_distance_m = (self._total_distance_m + to_accum)

    def _add_speed(self, speed):
        if speed is None:
            return

        self._max_speed_mps = (
            speed
            if self._max_speed_mps is None or speed > self._max_speed_mps
            else self._max_speed_mps
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


class Interval:

    def __init__(self, category: str):
        self._category = category

        self.distance_m = 0
        self.time_ms = 0

        self.avg_speed = 0
        self.max_speed = MaxSpeedNormalization.from_category(category)

        self.max_altitude = None
        self.min_altitude = None
        self.gain_elevation = None
        self.loss_elevation = None

        self.hr = SensorNormalization()
        self.cadence = SensorNormalization()

    @property
    def distance_str(self):
        return DistanceUtils.m_to_str(self.distance_m)

    @property
    def time_str(self):
        return TimeUtils.ms_to_str(self.time_ms)

    @property
    def avg_speed_str(self):
        return SpeedUtils.mps_to_category_rate(self.avg_speed, self._category)

    @property
    def max_speed_str(self):
        return SpeedUtils.mps_to_category_rate(self.max_speed.value_mps, self._category)

    @property
    def max_altitude_str(self):
        return ElevationUtils.elevation_to_str(self.max_altitude)

    @property
    def min_altitude_str(self):
        return ElevationUtils.elevation_to_str(self.min_altitude)

    @property
    def gain_elevation_str(self):
        return ElevationUtils.elevation_to_str(self.gain_elevation)

    @property
    def loss_elevation_str(self):
        return ElevationUtils.elevation_to_str(self.loss_elevation)

    @property
    def avg_hr_str(self):
        return SensorUtils.hr_to_str(self.hr.avg)

    @property
    def max_hr_str(self):
        return SensorUtils.hr_to_str(self.hr.max)

    @property
    def avg_cadence_str(self):
        return SensorUtils.hr_to_str(self.cadence.avg)

    @property
    def max_cadence_str(self):
        return SensorUtils.hr_to_str(self.cadence.max)


class IntervalStats:

    def __init__(self, category: str, distance_interval: float):
        """Create the interval stats class using an interval of distance_interval meters."""
        self._intervals: List[Interval] = []
        self._category: str = category
        self._distance_interval_m: float = distance_interval

    @property
    def intervals(self):
        return self._intervals

    def compute(self, track_points):
        interval = Interval(self._category)
        last_tp = track_points[0]
        for tp in track_points:
            interval.distance_m += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude, tp.latitude, tp.longitude
            )
            interval.time_ms += (tp.time_ms - last_tp.time_ms)
            interval.hr.add(tp.heart_rate, tp.time_ms)
            interval.cadence.add(tp.cadence, tp.time_ms)
            interval.max_speed.add(interval.distance_m, interval.time_ms)
            interval.gain_elevation = interval.gain_elevation + tp.elevation_gain if \
                interval.gain_elevation is not None else tp.elevation_gain
            interval.loss_elevation = interval.loss_elevation + tp.elevation_loss if \
                interval.loss_elevation is not None else tp.elevation_loss
            last_tp = tp

            if interval.distance_m >= self._distance_interval_m:
                adjust_factor = self._distance_interval_m / interval.distance_m
                accum_distance_m = interval.distance_m - self._distance_interval_m
                accum_time_ms = interval.time_ms - (interval.time_ms * adjust_factor)

                interval.distance_m *= adjust_factor
                interval.time_ms *= adjust_factor

                interval.avg_speed = interval.distance_m / (interval.time_ms / 1000)

                interval.distance_m = (len(self._intervals) + 1) * interval.distance_m

                self._intervals.append(interval)

                interval = Interval(self._category)
                interval.distance_m = accum_distance_m
                interval.time_ms = accum_time_ms

        if interval.distance_m > 10:
            interval.avg_speed = interval.distance_m / (interval.time_ms / 1000)
            interval.distance_m = len(self._intervals) * self._distance_interval_m + interval.distance_m
            self._intervals.append(interval)


class HrZonesStats:

    def __init__(self, zones: List[int]):
        """Class to compute stats on heart rate zones.

        Arguments:
        zones -- list of integers with heart rate zones.
        """
        self._zones = zones
        self._stats = {}
        self._total_time = 0
        for i, zone in enumerate(self._zones):
            self._stats[i] = 0

    def compute(self, sections: List[Section]):
        if sections is None or len(sections) == 0:
            return

        last_zone = -1
        for section in sections:
            last_tp = section.track_points[0]
            for tp in section.track_points:
                if last_zone > -1:
                    self._stats[last_zone] += (tp.time_ms - last_tp.time_ms)
                self._total_time += (tp.time_ms - last_tp.time_ms)
                last_tp = tp
                last_zone = self._get_zone_idx(last_tp.heart_rate)

        return self._stats

    @property
    def total_time(self):
        return self._total_time

    def _get_zone_idx(self, hr):
        if not hr:
            return -1
        idx = -1
        for value in self._zones:
            if hr < value:
                return idx
            idx += 1
        return idx

class MaxSpeedNormalization:

    def __init__(self):
        self.value_mps = 0

    @abstractmethod
    def add(self, distance_m, time_ms):
        pass

    @staticmethod
    def from_category(category: str):
        if TypeActivityUtils.is_speed(category):
            return MaxSpeedNormalizationNoFilter()
        else:
            return MaxSpeedNormalizationWithMinDistance()


class MaxSpeedNormalizationNoFilter(MaxSpeedNormalization):

    def __init__(self):
        super().__init__()
        self._last_distance_m = 0
        self._last_time_ms = 0

    def add(self, distance_m, time_ms):
        d = distance_m - self._last_distance_m
        t = time_ms - self._last_time_ms
        if t > 0:
            speed_mps = d / (t / 1000)

            self._last_distance_m = distance_m
            self._last_time_ms = time_ms

            if speed_mps > self.value_mps:
                self.value_mps = speed_mps


class MaxSpeedNormalizationWithMinDistance(MaxSpeedNormalization):

    MIN_DISTANCE_M = 50

    def __init__(self):
        super().__init__()
        self._last_distance_m = 0
        self._last_time_ms = 0
        self._accum_distance_m = 0
        self._accum_time_ms = 0

    def add(self, distance_m, time_ms):
        self._accum_distance_m += (distance_m - self._last_distance_m)
        self._accum_time_ms += (time_ms - self._last_time_ms)

        self._last_distance_m = distance_m
        self._last_time_ms = time_ms

        if self._accum_distance_m >= MaxSpeedNormalizationWithMinDistance.MIN_DISTANCE_M:
            avg_speed_mps = self._accum_distance_m / (self._accum_time_ms / 1000)
            if avg_speed_mps > self.value_mps:
                self.value_mps = avg_speed_mps
            self._accum_distance_m = 0
            self._accum_time_ms = 0


class SensorNormalization:

    def __init__(self):
        self._min = None
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

        self._min = self._compute_min(value)
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
    def min(self):
        if self._min:
            return round(self._min)
        return None

    @property
    def max(self):
        if self._max:
            return round(self._max)
        return None

    def _compute_min(self, new_value):
        if new_value is None:
            return self._min
        if self._min is None:
            return new_value
        if new_value < self._min:
            return new_value
        else:
            return self._min

    def _compute_max(self, new_value):
        if new_value is None:
            return self._max
        if self._max is None:
            return new_value
        if new_value > self._max:
            return new_value
        else:
            return self._max

