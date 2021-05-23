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

from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import DistanceUtils as du
from pyopentracks.utils.utils import SpeedUtils as su
from pyopentracks.utils.utils import ElevationUtils as eu
from pyopentracks.utils.utils import SensorUtils as se
from pyopentracks.utils.utils import TypeActivityUtils as tau


class AggregatedStats:
    def __init__(self, *args):
        self._category = args[0]
        self._total_activities = args[1]
        self._total_time_ms = args[2]
        self._total_moving_time_ms = args[3]
        self._total_distance_m = args[4]
        self._total_elevation_gain_m = args[5]
        self._avg_time_ms = args[6]
        self._avg_moving_time_ms = args[7]
        self._avg_distance_m = args[8]
        self._avg_elevation_gain_m = args[9]
        self._avg_speed_mps = args[10]
        self._avg_heart_rate_bpm = args[11]
        self._max_time_ms = args[12]
        self._max_moving_time_ms = args[13]
        self._max_distance_m = args[14]
        self._max_elevation_gain_m = args[15]
        self._max_speed_mps = args[16]
        self._max_heart_rate_bpm = args[17]

    @property
    def category(self):
        return self._category

    @property
    def total_activities(self):
        return self._total_activities

    @property
    def total_time(self):
        return tu.ms_to_str(self._total_time_ms)

    @property
    def total_moving_time(self):
        return tu.ms_to_str(self._total_moving_time_ms)

    @property
    def total_distance(self):
        return du.m_to_str(self._total_distance_m)

    @property
    def total_distance_float(self):
        return self._total_distance_m / 1000

    @property
    def total_elevation_gain(self):
        return eu.elevation_to_str(self._total_elevation_gain_m)

    @property
    def avg_time(self):
        return tu.ms_to_str(self._avg_time_ms)

    @property
    def avg_moving_time(self):
        return tu.ms_to_str(self._avg_moving_time_ms)

    @property
    def avg_distance(self):
        return du.m_to_str(self._avg_distance_m)

    @property
    def avg_elevation_gain(self):
        return eu.elevation_to_str(self._avg_elevation_gain_m)

    @property
    def avg_speed(self):
        return su.mps_to_category_rate(self._avg_speed_mps, self._category)

    @property
    def avg_heart_rate(self):
        return se.hr_to_str(self._avg_heart_rate_bpm)

    @property
    def max_time(self):
        return tu.ms_to_str(self._max_time_ms)

    @property
    def max_moving_time(self):
        return tu.ms_to_str(self._max_moving_time_ms)

    @property
    def max_distance(self):
        return du.m_to_str(self._max_distance_m)

    @property
    def max_elevation_gain(self):
        return eu.elevation_to_str(self._max_elevation_gain_m)

    @property
    def max_speed(self):
        return su.mps_to_category_rate(self._max_speed_mps, self._category)

    @property
    def max_heart_rate(self):
        return se.hr_to_str(self._max_heart_rate_bpm)

    @property
    def activities_label(self):
        return _("Activities")

    @property
    def time_label(self):
        return _("Time")

    @property
    def moving_time_label(self):
        return _("Moving Time")

    @property
    def distance_label(self):
        return _("Distance")

    @property
    def elevation_gain_label(self):
        return _("Elevation Gain")

    @property
    def speed_label(self):
        return _("Speed") if tau.is_speed(self._category) else _("Pace")

    @property
    def heart_rate_label(self):
        return _("Heart Rate")