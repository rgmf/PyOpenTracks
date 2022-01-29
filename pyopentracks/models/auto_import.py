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


class AutoImport(Model):
    def __init__(self, *args):
        self._id = args[0]
        self._trackfile = args[1]
        self._result = args[2]

    @property
    def insert_query(self):
        """Returns the query for inserting a AutoImport register."""
        return "INSERT INTO autoimport VALUES (?, ?, ?)"

    @property
    def delete_query(self):
        """Returns the query for deleting an AutoImport by id."""
        return "DELETE FROM autoimport WHERE _id=?"

    @property
    def update_query(self):
        """Return the query for updating a Track by id."""
        return """
        UPDATE autoimport SET trackfile=?, result=?
        WHERE _id=?
        """

    @property
    def update_data(self):
        return (self._trackfile, self._result, self._id)

    @property
    def fields(self):
        """Returns a tuple with all AutoImport fields.
        Maintain the database table autoimport order of the fields.
        """
        return (self._id, self._trackfile, self._result)

    @property
    def bulk_insert_fields(self, fk_value):
        pass
