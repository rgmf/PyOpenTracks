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

from .model import Model
from pyopentracks.models.track_point import TrackPoint


class Section(Model):

    __slots__ = ("_id", "_name", "_activity_id", "_track_points")

    def __init__(self, *args):
        super().__init__()
        self._id = args[0] if args else None
        self._name = args[1] if args else None
        self._activity_id = args[2] if args else None

        self._track_points: List[TrackPoint] = []

    @property
    def insert_query(self):
        return """
        INSERT INTO sections VALUES (?, ?, ?)
        """

    @property
    def delete_query(self):
        return "DELETE FROM sections WHERE _id=?"

    @property
    def update_query(self):
        pass

    @property
    def update_data(self):
        pass

    @property
    def fields(self):
        return (self._id, self._name, self._activity_id)

    def bulk_insert_fields(self, fk_value):
        pass

    @property
    def id(self):
        return self._id

    @property
    def activity_id(self):
        return self._activity_id

    @activity_id.setter
    def activity_id(self, activity_id):
        self._activity_id = activity_id

    @property
    def track_points(self):
        return self._track_points
