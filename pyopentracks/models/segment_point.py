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

from .model import Model


class SegmentPoint(Model):

    def __init__(self, *args):
        self._id = args[0] if args else None
        self._segmentid = args[1] if args else None
        self._latitude = args[2] if args else None
        self._longitude = args[3] if args else None
        self._altitude = args[4] if args else None

    @property
    def insert_query(self):
        """Returns the query for inserting a SegmentPoint register."""
        return "INSERT INTO segmentpoints VALUES (?, ?, ?, ?, ?)"

    @property
    def delete_query(self):
        """Returns the query for deleting a SegmentPoint by id."""
        return "DELETE FROM segmentpoints WHERE _id=?"

    @property
    def update_query(self):
        """Returns the query for updating a SegmentPoint by id."""
        return "UPDATE segmentpoints SET segmentid=?, latitude=?, longitude=?, altitude=? WHERE _id=?"

    @property
    def update_data(self):
        return (
            self._segmentid,
            self._latitude,
            self._longitude,
            self._altitude
        )

    @property
    def fields(self):
        """Returns a tuple with all Segment fields.
        Maintain the database table segments order of the fields."""
        return (
            self._id,
            self._segmentid,
            self._latitude,
            self._longitude,
            self._altitude
        )

    def bulk_insert_fields(self, fk_value):
        """Returns a tuple with all SegmentPoint fields.
        the segmentid's value is in fk_value argument."""
        return (
            self._id,
            fk_value,
            self._latitude,
            self._longitude,
            self._altitude
        )

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def altitude(self):
        return self._altitude
