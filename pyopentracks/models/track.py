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

from os import path

from .model import Model
from pyopentracks.settings import xdg_data_home
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import DistanceUtils as du
from pyopentracks.utils.utils import SpeedUtils as su
from pyopentracks.utils.utils import ElevationUtils as eu
from pyopentracks.utils.utils import SensorUtils as se
from pyopentracks.utils.utils import TypeActivityUtils as tau


class Track(Model):
    def __init__(self, *args):
        self._id = args[0]
        self._trackfile = args[1]
        self._uuid = args[2]
        self._name = args[3]
        self._description = args[4]
        self._category = args[5]
        self._starttime_ms = args[6]
        self._stoptime_ms = args[7]
        self._totaldistance_m = args[8]
        self._totaltime_ms = args[9]
        self._movingtime_ms = args[10]
        self._avgspeed_mps = args[11]
        self._avgmovingspeed_mps = args[12]
        self._maxspeed_mps = args[13]
        self._minelevation_m = args[14]
        self._maxelevation_m = args[15]
        self._elevationgain_m = args[16]
        self._elevationloss_m = args[17]
        self._maxhr_bpm = args[18]
        self._avghr_bpm = args[19]
        self._maxcadence_rpm = args[20]
        self._avgcadence_rpm = args[21]

        self._track_points = None

    def add_track_stats(self, ts):
        """Add TrackStats object and complete track data.

        Arguments:
        ts -- TrackStats object.
        """
        self._track_points = ts.track_points
        self._starttime_ms = ts.start_time
        self._stoptime_ms = ts.end_time
        self._totaldistance_m = ts.total_distance
        self._totaltime_ms = ts.total_time
        self._movingtime_ms = ts.moving_time
        self._avgspeed_mps = ts.avg_speed
        self._avgmovingspeed_mps = ts.avg_moving_speed
        self._maxspeed_mps = ts.max_speed
        self._minelevation_m = ts.min_elevation
        self._maxelevation_m = ts.max_elevation
        self._elevationgain_m = ts.gain_elevation
        self._elevationloss_m = ts.loss_elevation
        self._maxhr_bpm = ts.max_hr
        self._avghr_bpm = ts.avg_hr
        self._avgcadence_rpm = ts.avg_cadence
        self._maxcadence_rpm = ts.max_cadence

    @property
    def insert_query(self):
        """Returns the query for inserting a Track register."""
        return """
        INSERT INTO tracks VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """

    @property
    def delete_query(self):
        """Returns the query for deleting a Track by id."""
        return "DELETE FROM tracks WHERE _id=?"

    @property
    def update_query(self):
        """Return the query for updating a Track by id."""
        return """
        UPDATE tracks 
        SET name=?, description=?, category=?, minelevation=?, maxelevation=?, elevationgain=?, elevationloss=?
        WHERE _id=?
        """

    @property
    def update_data(self):
        return (
            self._name,
            self._description,
            self._category,
            self._minelevation_m,
            self._maxelevation_m,
            self._elevationgain_m,
            self._elevationloss_m,
            self._id
        )

    @property
    def fields(self):
        """Returns a tuple with all Track fields.
        Maintain the database table tracks order of the fields.
        """
        return (
            self._id,
            self._trackfile,
            self._uuid,
            self._name,
            self._description,
            self._category,
            self._starttime_ms,
            self._stoptime_ms,
            self._totaldistance_m,
            self._totaltime_ms,
            self._movingtime_ms,
            self._avgspeed_mps,
            self._avgmovingspeed_mps,
            self._maxspeed_mps,
            self._minelevation_m,
            self._maxelevation_m,
            self._elevationgain_m,
            self._elevationloss_m,
            self._maxhr_bpm,
            self._avghr_bpm,
            self._maxcadence_rpm,
            self._avgcadence_rpm
        )

    def bulk_insert_fields(self, fk_value):
        pass

    @property
    def id(self):
        return self._id

    @property
    def uuid(self):
        return self._uuid

    @property
    def trackfile_path(self):
        return path.join(xdg_data_home(), self._trackfile)

    def set_trackfile_path(self, tfp: str):
        self._trackfile = tfp

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description if self._description else ""

    @property
    def activity_type(self):
        return self._category

    @property
    def track_points(self):
        return self._track_points

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
    def total_distance(self):
        return du.m_to_str(self._totaldistance_m)

    @property
    def total_distance_label(self):
        return _("Distance")

    @property
    def avg_speed(self):
        return su.mps_to_category_rate(self._avgspeed_mps, self._category)

    @property
    def avg_speed_label(self):
        return _("Avg. Speed") if tau.is_speed(self._category) else _("Avg. Pace")

    @property
    def max_speed(self):
        return su.mps_to_category_rate(self._maxspeed_mps, self._category)

    @property
    def max_speed_label(self):
        return _("Max. Speed") if tau.is_speed(self._category) else _("Max. Pace")

    @property
    def avg_moving_speed(self):
        return su.mps_to_category_rate(self._avgmovingspeed_mps, self._category)

    @property
    def avg_moving_speed_label(self):
        return _("Avg. Moving Speed") if tau.is_speed(self._category) else _("Avg. Moving Pace")

    @property
    def max_elevation(self):
        return eu.elevation_to_str(self._maxelevation_m)

    @property
    def max_elevation_label(self):
        return _("Max. Altitude")

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
    def gain_elevation_label(self):
        return _("Elevation Gain")

    @property
    def loss_elevation(self):
        return eu.elevation_to_str(self._elevationloss_m)

    @property
    def loss_elevation_label(self):
        return _("Elevation Loss")

    @property
    def max_hr(self):
        return se.hr_to_str(self._maxhr_bpm)

    @property
    def max_hr_label(self):
        return _("Max. Heart Rate")

    @property
    def avg_hr(self):
        return se.hr_to_str(self._avghr_bpm)

    @property
    def avg_hr_label(self):
        return _("Avg. Heart Rate")

    @property
    def max_cadence(self):
        return se.cadence_to_str(self._maxcadence_rpm)

    @property
    def max_cadence_label(self):
        return _("Max. Cadence")

    @property
    def avg_cadence(self):
        return se.cadence_to_str(self._avgcadence_rpm)

    @property
    def avg_cadence_label(self):
        return _("Avg. Cadence")

    def set_name(self, new_name):
        self._name = new_name

    def set_description(self, new_desc):
        self._description = new_desc

    def set_activity_type(self, new_category):
        self._category = new_category

    def set_gain(self, gain):
        self._elevationgain_m = gain

    def set_loss(self, loss):
        self._elevationloss_m = loss

    def set_max_altitude(self, altitude):
        self._maxelevation_m = altitude

    def set_min_altitude(self, altitude):
        self._minelevation_m = altitude
