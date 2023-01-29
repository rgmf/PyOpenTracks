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
from dataclasses import dataclass
from itertools import chain
from typing import List

from .model import Model
from pyopentracks.models.section import Section
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.models.stats import Stats
from pyopentracks.io.parser.recorded_with import RecordedOptions, RecordedWith


class MultiActivity:

    __slots__ = ("sequence",)

    @dataclass
    class Data:
        value: any

        @property
        def is_transition(self) -> bool:
            return not self.is_activity

        @property
        def is_activity(self) -> bool:
            return isinstance(self.value, Activity)

        @property
        def category(self) -> str:
            return "transition" if self.is_transition else self.value.category

        @property
        def time(self) -> str:
            return self.value.stats.moving_time if self.is_activity else tu.ms_to_str(self.value)

        @property
        def speed(self) -> str:
            return self.value.stats.avg_moving_speed(self.value.category) if self.is_activity else ""

    def __init__(self, activity):
        self.sequence: List[MultiActivity.Data] = []

        prev_a = None
        for a in activity.activities:
            if prev_a is not None:
                transition_ms = a.stats.start_time_ms - prev_a.stats.end_time_ms
                self.sequence.append(MultiActivity.Data(transition_ms))
            prev_a = a
            self.sequence.append(MultiActivity.Data(a))


class Activity(Model):
    __slots__ = (
        "_id", "_uuid", "_name", "_description", "_category", "_recorded_with",
        "_start_time_ms", "_stats_id", "_activity_id", "_stats", "_sections",
        "_activities"
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
        self._activity_id = args[8] if args else None

        self._stats: Stats = Stats(*args[9:]) if args and len(args) > 9 else None
        self._sections: List[Section] = []
        self._activities: List[Activity] = []

    def __repr__(self):
        return f"Activity(id={self._id!r}, uuid={self._uuid!r}, name={self._name!r}, " \
            f"description={self._description!r}, category={self._category!r}, " \
            f"recorded_with={self._recorded_with!r}, start_time_ms={self._start_time_ms!r}, " \
            f"stats_id={self._stats_id!r}, activity_id={self._activity_id!r}, " \
            f"stats={self._stats!r}, sections={self._sections!r}, activities={self._activities!r})"

    @property
    def insert_query(self):
        """Returns the query for inserting an Activity register."""
        return """
        INSERT INTO activities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            self._stats_id, self._activity_id
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

    @property
    def activity_id(self):
        return self._activity_id

    @property
    def activities(self):
        return self._activities

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

    @activity_id.setter
    def activity_id(self, id):
        self._activity_id = id

    @activities.setter
    def activities(self, activities):
        self._activities = activities
