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

from itertools import chain
from typing import List

from .model import Model
from pyopentracks.models.section import Section
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.models.stats import Stats
from pyopentracks.io.parser.recorded_with import RecordedOptions, RecordedWith


class Activity(Model):
    __slots__ = (
        "_id", "_uuid", "_name", "_description", "_category", "_recorded_with",
        "_start_time_ms", "_stats_id", "_stats", "_sections"
    )

    def __init__(self, *args):
        super().__init__()
        self._id = args[0] if args else None
        self._uuid = args[1] if args else None
        self._name = args[2] if args else None
        self._description = args[3] if args else None
        self._category = args[4] if args else None
        self._recorded_with = args[5] if args else None
        self._start_time_ms = args[6] if args else None
        self._stats_id = args[7] if args else None

        self._stats: Stats = Stats(*args[8:]) if args and len(args) > 8 else None
        self._sections: List[Section] = []

    @property
    def insert_query(self):
        """Returns the query for inserting an Activity register."""
        return """
        INSERT INTO activities VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

    @property
    def delete_query(self):
        """Returns the query for deleting a Activity by id."""
        return "DELETE FROM activities WHERE _id=?"

    @property
    def update_query(self):
        """Return the query for updating a Activity by id."""
        return """
        UPDATE activities 
        SET name=?, description=?, category=?
        WHERE _id=?
        """

    @property
    def update_data(self):
        return (self._name, self._description, self._category, self._id)

    @property
    def fields(self):
        """Returns a tuple with all Activity fields.
        Maintain the database table activities order of the fields.
        """
        return (
            self._id, self._uuid, self._name, self._description,
            self._category, self._recorded_with, self._start_time_ms, 
            self._stats_id
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
    def stats_id(self):
        return self._stats_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description if self._description else ""

    @property
    def category(self):
        return self._category

    @property
    def recorded_with(self) -> RecordedWith:
        if self._recorded_with is None or self._recorded_with not in RecordedOptions:
            return RecordedWith.unknown()
        return RecordedOptions[self._recorded_with]

    @property
    def start_time(self):
        return dtu.ms_to_str(self._start_time_ms)

    @property
    def start_time_ms(self):
        return self._start_time_ms

    @property
    def stats(self):
        return self._stats

    @property
    def sections(self):
        return self._sections

    @property
    def all_track_points(self):
        """Return a list of all track points from all sections"""
        if not self.sections:
            return []
        return list(chain(*[ section.track_points for section in self.sections ]))

    @stats_id.setter
    def stats_id(self, stats_id):
        self._stats_id = stats_id

    @name.setter
    def name(self, name):
        self._name = name

    @description.setter
    def description(self, description):
        self._description = description

    @category.setter
    def category(self, category):
        self._category = category

    @stats.setter
    def stats(self, stats):
        self._stats = stats

    @sections.setter
    def sections(self, sections):
        self._sections = sections

    @recorded_with.setter
    def recorded_with(self, recorded_with):
        self._recorded_with = recorded_with
