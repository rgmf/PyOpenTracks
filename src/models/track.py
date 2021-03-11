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

    @property
    def insert_query(self):
        """Returns the query for inserting a Track register."""
        return """
        INSERT INTO tracks VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """

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
        )

    @property
    def uuid(self):
        return self._uuid

    @property
    def trackfile_path(self):
        return path.join(xdg_data_home(), self._trackfile)

    def set_trackfile_path(self, tfp: str):
        self._trackfile = tfp

    def set_autoimportfile_path(self, path: str):
        self._autoimportfile = path

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

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
    def start_time_ms(self):
        return self._starttime_ms

    @property
    def end_time(self):
        return dtu.ms_to_str(self._stoptime_ms)

    @property
    def end_time_ms(self):
        return self._stoptime_ms

    @property
    def total_time(self):
        return tu.ms_to_str(self._totaltime_ms)

    @property
    def moving_time(self):
        return tu.ms_to_str(self._movingtime_ms)

    @property
    def total_distance(self):
        return du.m_to_str(self._totaldistance_m)

    @property
    def avg_speed(self):
        return su.mps_to_kph(self._avgspeed_mps)

    @property
    def max_speed(self):
        return su.mps_to_kph(self._maxspeed_mps)

    @property
    def avg_moving_speed(self):
        return su.mps_to_kph(self._avgmovingspeed_mps)

    @property
    def max_elevation(self):
        return eu.elevation_to_str(self._maxelevation_m)

    @property
    def min_elevation(self):
        return eu.elevation_to_str(self._minelevation_m)

    @property
    def gain_elevation(self):
        return eu.elevation_to_str(self._elevationgain_m)

    @property
    def loss_elevation(self):
        return eu.elevation_to_str(self._elevationloss_m)
