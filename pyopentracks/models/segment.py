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
from pyopentracks.utils.utils import DistanceUtils, ElevationUtils


class Segment(Model):

    def __init__(self, *args):
        self._id = args[0] if args else None
        self._name = args[1] if args else None
        self._distance_m = args[2] if args else None
        self._gain_m = args[3] if args else None
        self._loss_m = args[4] if args else None

    @property
    def insert_query(self):
        """Returns the query for inserting a Segment register."""
        return "INSERT INTO segments VALUES (?, ?, ?, ?, ?)"

    @property
    def delete_query(self):
        """Returns the query for deleting a Segment by id."""
        return "DELETE FROM segments WHERE _id=?"

    @property
    def update_query(self):
        """Returns the query for updating a Segment by id."""
        return "UPDATE segments SET name=?, distance=?, gain=?, loss=? WHERE _id=?"

    @property
    def update_data(self):
        return (
            self._name,
            self._distance_m,
            self._gain_m,
            self._loss_m
        )

    @property
    def fields(self):
        """Returns a tuple with all Segment fields.
        Maintain the database table segments order of the fields."""
        return (
            self._id,
            self._name,
            self._distance_m,
            self._gain_m,
            self._loss_m
        )

    def bulk_insert_fields(self, fk_value):
        pass

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def distance_m(self):
        return self._distance_m

    @property
    def distance(self):
        return DistanceUtils.m_to_str(self._distance_m)

    @property
    def gain_m(self):
        return self._gain_m

    @property
    def gain(self):
        return ElevationUtils.elevation_to_str(self._gain_m)

    @property
    def loss_m(self):
        return self._loss_m

    @property
    def loss(self):
        return ElevationUtils.elevation_to_str(self._loss_m)

    @property
    def slope(self):
        if self._distance_m and self._gain_m:
            return ElevationUtils.slope_to_str(self._gain_m * 100 / self._distance_m)
        else:
            return "-"

    @id.setter
    def id(self, id):
        self._id = id