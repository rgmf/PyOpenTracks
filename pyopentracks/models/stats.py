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
from typing import List

from pyopentracks.models.set import Set
from .model import Model
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import DistanceUtils as du
from pyopentracks.utils.utils import SpeedUtils as su
from pyopentracks.utils.utils import ElevationUtils as eu
from pyopentracks.utils.utils import SensorUtils as se
from pyopentracks.utils.utils import TypeActivityUtils as tau


class Stats(Model):
    __slots__ = (
        "_id", "_starttime_ms", "_stoptime_ms", "_totaldistance_m",
        "_totaltime_ms", "_movingtime_ms", "_avgspeed_mps",
        "_avgmovingspeed_mps", "_maxspeed_mps", "_minelevation_m",
        "_maxelevation_m", "_elevationgain_m", "_elevationloss_m",
        "_maxhr_bpm", "_avghr_bpm", "_maxcadence_rpm",
        "_avgcadence_rpm", "_power_normalized_w", "_power_max_w",
        "_avg_temperature", "_max_temperature", "_total_calories"
    )

    def __init__(self, *args) -> None:
        super().__init__()
        self._id = args[0] if args else None
        self._starttime_ms = args[1] if args else None
        self._stoptime_ms = args[2] if args else None
        self._totaldistance_m = args[3] if args else None
        self._totaltime_ms = args[4] if args else None
        self._movingtime_ms = args[5] if args else None
        self._avgspeed_mps = args[6] if args else None
        self._avgmovingspeed_mps = args[7] if args else None
        self._maxspeed_mps = args[8] if args else None
        self._minelevation_m = args[9] if args else None
        self._maxelevation_m = args[10] if args else None
        self._elevationgain_m = args[11] if args else None
        self._elevationloss_m = args[12] if args else None
        self._maxhr_bpm = args[13] if args else None
        self._avghr_bpm = args[14] if args else None
        self._maxcadence_rpm = args[15] if args else None
        self._avgcadence_rpm = args[16] if args else None
        self._power_normalized_w = args[17] if args else None
        self._power_max_w = args[18] if args else None
        self._avg_temperature = args[19] if args else None
        self._max_temperature = args[20] if args else None
        self._total_calories = args[21] if args else None

        self._sets: List[Set] = []

    @property
    def insert_query(self):
        """Returns the query for inserting a Stats register."""
        return """
        INSERT INTO stats VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """

    @property
    def delete_query(self):
        """Returns the query for deleting a Stats by id."""
        return "DELETE FROM stats WHERE _id=?"

    @property
    def update_query(self):
        pass

    @property
    def update_data(self):
        pass

    @property
    def fields(self):
        return (
            self._id, self._starttime_ms, self._stoptime_ms,
            self._totaldistance_m, self._totaltime_ms, self._movingtime_ms,
            self._avgspeed_mps, self._avgmovingspeed_mps, self._maxspeed_mps,
            self._minelevation_m, self._maxelevation_m, self._elevationgain_m,
            self._elevationloss_m, self._maxhr_bpm, self._avghr_bpm,
            self._maxcadence_rpm, self._avgcadence_rpm, self._power_normalized_w,
            self._power_max_w, self._avg_temperature, self._max_temperature,
            self._total_calories
        )

    def bulk_insert_fields(self, fk_value):
        pass

    @property
    def id(self):
        return self._id

    @property
    def start_time(self):
        return dtu.ms_to_str(self._starttime_ms)

    @property
    def short_start_time(self):
        return dtu.ms_to_str(self._starttime_ms, short=True)

    @property
    def start_time_ms(self):
        return self._starttime_ms

    @property
    def start_time_label(self):
        return _("Start")

    @property
    def end_time(self):
        return dtu.ms_to_str(self._stoptime_ms)

    @property
    def end_time_ms(self):
        return self._stoptime_ms

    @property
    def end_time_label(self):
        return _("End")

    @property
    def total_time(self):
        return tu.ms_to_str(self._totaltime_ms)

    @property
    def total_time_label(self):
        return _("Total Time")

    @property
    def moving_time(self):
        return tu.ms_to_str(self._movingtime_ms)

    @property
    def moving_time_label(self):
        return _("Moving Time")

    @property
    def total_distance_m(self):
        return self._totaldistance_m

    @property
    def total_distance(self):
        return du.m_to_str(self._totaldistance_m)

    @property
    def total_distance_label(self):
        return _("Distance")

    @property
    def sets(self):
        return self._sets

    def avg_speed(self, category):
        return su.mps_to_category_rate(self._avgspeed_mps, category)

    def speed_label(self, category):
        return _("Speed") if tau.is_speed(category) else _("Pace")

    def avg_speed_label(self, category):
        return _("Avg. Speed") if tau.is_speed(category) else _("Avg. Pace")

    def max_speed(self, category):
        return su.mps_to_category_rate(self._maxspeed_mps, category)

    def max_speed_label(self, category):
        return _("Max. Speed") if tau.is_speed(category) else _("Max. Pace")

    def avg_moving_speed(self, category):
        return su.mps_to_category_rate(self._avgmovingspeed_mps, category)

    def avg_moving_speed_label(self, category):
        return _("Avg. Moving Speed") if tau.is_speed(category) else _("Avg. Moving Pace")

    @property
    def max_elevation_m(self):
        return self._maxelevation_m

    @property
    def max_elevation(self):
        return eu.elevation_to_str(self._maxelevation_m)

    @property
    def max_elevation_label(self):
        return _("Max. Altitude")

    @property
    def min_elevation_m(self):
        return self._minelevation_m

    @property
    def min_elevation(self):
        return eu.elevation_to_str(self._minelevation_m)

    @property
    def min_elevation_label(self):
        return _("Min. Altitude")

    @property
    def gain_elevation(self):
        return eu.elevation_to_str(self._elevationgain_m)

    @property
    def gain_elevation_m(self):
        return self._elevationgain_m

    @property
    def gain_elevation_label(self):
        return _("Elevation Gain")

    @property
    def loss_elevation(self):
        return eu.elevation_to_str(self._elevationloss_m)

    @property
    def loss_elevation_m(self):
        return self._elevationloss_m

    @property
    def loss_elevation_label(self):
        return _("Elevation Loss")

    @property
    def max_hr_bpm(self):
        return self._maxhr_bpm

    @property
    def max_hr(self):
        return se.hr_to_str(self._maxhr_bpm)

    @property
    def max_hr_label(self):
        return _("Max. Heart Rate")

    @property
    def avg_hr_bpm(self):
        return self._avghr_bpm

    @property
    def avg_hr(self):
        return se.hr_to_str(self._avghr_bpm)

    @property
    def avg_hr_label(self):
        return _("Avg. Heart Rate")

    @property
    def max_cadence_rpm(self):
        return self._maxcadence_rpm

    def max_cadence(self, category: str):
        return se.cadence_to_str(self._maxcadence_rpm, category)

    @property
    def max_cadence_label(self):
        return _("Max. Cadence")

    @property
    def avg_cadence_rpm(self):
        return self._avgcadence_rpm

    def avg_cadence(self, category: str):
        return se.cadence_to_str(self._avgcadence_rpm, category)

    @property
    def avg_cadence_label(self):
        return _("Avg. Cadence")

    @property
    def power_normalized(self):
        return self._power_normalized_w

    @property
    def power_normalized_label(self):
        return _("Normalized Power")

    @property
    def power_max(self):
        return self._power_max_w

    @property
    def power_max_label(self):
        return _("Max. Power")

    @property
    def avg_temperature_label(self):
        return _("Avg. Temperature")

    @property
    def avg_temperature_value(self):
        return self._avg_temperature

    @property
    def avg_temperature(self):
        return se.temperature_to_str(self._avg_temperature)

    @property
    def max_temperature_label(self):
        return _("Max. Temperature")

    @property
    def max_temperature_value(self):
        return self._max_temperature

    @property
    def max_temperature(self):
        return se.temperature_to_str(self._max_temperature)

    @property
    def total_calories_label(self):
        return _("Total Calories")

    @property
    def total_calories_value(self):
        return self._total_calories

    @property
    def total_calories(self):
        return se.calories_to_str(self._total_calories)

    @gain_elevation_m.setter
    def gain_elevation_m(self, gain):
        self._elevationgain_m = gain

    @loss_elevation_m.setter
    def loss_elevation_m(self, loss):
        self._elevationloss_m = loss

    @max_elevation_m.setter
    def max_elevation_m(self, elevation):
        self._maxelevation_m = elevation

    @min_elevation_m.setter
    def min_elevation_m(self, elevation):
        self._minelevation_m = elevation

    @sets.setter
    def sets(self, sets):
        self._sets = sets
