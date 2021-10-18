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

from .model import Model


class TrackPoint(Model):

    def __init__(self, *args):
        self._id = args[0] if args else None
        self._trackid = args[1] if args else None
        self._longitude = args[2] if args else None
        self._latitude = args[3] if args else None
        self._time_ms = args[4] if args else None
        self._speed_mps = args[5] if args else None
        self._altitude_m = args[6] if args else None
        self._elevation_gain_m = args[7] if args else None
        self._elevation_loss_m = args[8] if args else None
        self._heart_rate_bpm = args[9] if args else None
        self._cadence_rpm = args[10] if args else None
        self._power_w = args[11] if args else None

    @property
    def insert_query(self):
        """Returns the query for inserting a TrackPoint register."""
        return """
        INSERT INTO trackpoints VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """

    @property
    def delete_query(self):
        """Returns the query for deleting a TrackPoint by id."""
        return "DELETE FROM trackpoints WHERE _id=?"

    @property
    def update_query(self):
        """Returns the query for updating a TrackPoint by id."""
        return """
        UPDATE trackpoints SET longitude=?, latitude=?, time=?, speed=?, altitude=?,
        gain=?, loss=?, heartrate=?, cadence=?, power=?
        WHERE _id=?
        """

    @property
    def update_data(self):
        return (
            self._longitude, self._latitude, self._time_ms, self._speed_mps,
            self._altitude_m, self._elevation_gain_m, self._elevation_loss_m,
            self._heart_rate_bpm, self._cadence_rpm, self._power_w, self._id
        )

    @property
    def fields(self):
        """Returns a tuple with all TrackPoint fields.
        Maintain the database table trackpoints order of the fields."""
        return (
            self._id,
            self._trackid,
            self._longitude,
            self._latitude,
            self._time_ms,
            self._speed_mps,
            self._altitude_m,
            self._elevation_gain_m,
            self._elevation_loss_m,
            self._heart_rate_bpm,
            self._cadence_rpm,
            self._power_w
        )

    def bulk_insert_fields(self, fk_value):
        """Returns a tuple with all TrackPoint fields.
        the trackid's value is in fk_value argument."""
        return (
            self._id,
            fk_value,
            self._longitude,
            self._latitude,
            self._time_ms,
            self._speed_mps,
            self._altitude_m,
            self._elevation_gain_m,
            self._elevation_loss_m,
            self._heart_rate_bpm,
            self._cadence_rpm,
            self._power_w
        )

    @property
    def id(self):
        return self._id

    @property
    def location_tuple(self):
        """Build and return a tuple object representing location."""
        return (float(self._latitude), float(self._longitude))

    @property
    def longitude(self):
        if self._longitude:
            return float(self._longitude)
        return 0

    @property
    def latitude(self):
        if self._latitude:
            return float(self._latitude)
        return 0

    @property
    def speed(self):
        if self._speed_mps:
            return float(self._speed_mps)
        return 0

    @property
    def altitude(self):
        if self._altitude_m:
            return float(self._altitude_m)
        return 0

    @property
    def elevation_gain(self):
        if self._elevation_gain_m:
            return float(self._elevation_gain_m)
        return 0

    @property
    def elevation_loss(self):
        if self._elevation_loss_m:
            return float(self._elevation_loss_m)
        return 0

    @property
    def heart_rate(self):
        if self._heart_rate_bpm:
            return float(self._heart_rate_bpm)
        return 0

    @property
    def cadence(self):
        if self._cadence_rpm:
            return float(self._cadence_rpm)
        return 0

    @property
    def time_ms(self):
        return self._time_ms

    @property
    def speed_mps(self):
        return self._speed_mps

    def set_latitude(self, latitude):
        self._latitude = latitude

    def set_longitude(self, longitude):
        self._longitude = longitude

    def set_trackid(self, trackid):
        self._trackid = trackid

    def set_altitude(self, altitude):
        self._altitude_m = altitude

    def set_elevation_gain(self, gain):
        self._elevation_gain_m = gain

    def set_elevation_loss(self, loss):
        self._elevation_loss_m = loss

    def set_time(self, time):
        self._time_ms = time

    def set_speed(self, speed):
        self._speed_mps = speed

    def set_heart_rate(self, hr):
        self._heart_rate_bpm = hr

    def set_cadence(self, cadence):
        self._cadence_rpm = cadence