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
from pyopentracks.io.parser.fit.messages import EXERCISE_CATEGORY, SetType, SetResult
from pyopentracks.utils.utils import SensorUtils, TimeUtils
from .model import Model


class Set(Model):
    __slots__ = (
        "_id", "type", "result", "exercise_category", "weight", "repetitions",
        "avghr", "maxhr", "time", "calories", "temperature", "difficulty",
        "stats_id"
    )

    DIFFICULTIES = [
        "1", "2", "3", "4", "4+", "5", "5+",
        "6A", "6A+", "6B", "6B+", "6C", "6C+",
        "7A", "7A+", "7B", "7B+", "7C", "7C+",
        "8A", "8A+", "8B", "8B+", "8C", "8C+",
        "9A"
    ]

    def __init__(self, *args):
        super().__init__()
        self._id = args[0] if args else None
        self.type = args[1] if args else None
        self.result = args[2] if args else None
        self.exercise_category = args[3] if args else None
        self.weight = args[4] if args else None
        self.repetitions = args[5] if args else None
        self.avghr = args[6] if args else None
        self.maxhr = args[7] if args else None
        self.time = args[8] if args else None
        self.calories = args[9] if args else None
        self.temperature = args[10] if args else None
        self.difficulty = args[11] if args else None
        self.stats_id = args[12] if args else None

    @property
    def insert_query(self):
        """Returns the query for inserting a Set register."""
        return """
        INSERT INTO sets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    @property
    def delete_query(self):
        """Returns the query for deleting a Set by id."""
        return "DELETE FROM sets WHERE _id=?"

    @property
    def update_query(self):
        pass

    @property
    def update_data(self):
        pass

    @property
    def fields(self):
        """Returns a tuple with all Set fields.
        Maintain the database table sets order of the fields.
        """
        return (
            self._id, self.type, self.result, self.exercise_category, self.weight,
            self.repetitions, self.avghr, self.maxhr, self.time,
            self.calories, self.temperature, self.difficulty,
            self.stats_id
        )

    def bulk_insert_fields(self, fk_value):
        pass

    @property
    def type_label(self):
        return _("Set Type")

    def type_value(self, active_label=_("Active"), resting_label=_("Resting")):
        return resting_label if SetType.REST.value == self.type else active_label

    @property
    def result_label(self):
        return _("Result")

    @property
    def result_value(self):
        if self.result == SetResult.COMPLETED.value:
            return _("Completed")
        if self.result == SetResult.ATTEMPTED.value:
            return _("Attempted")
        if self.result == SetResult.DISCARDED.value:
            return _("Discarded")
        return "-"

    @property
    def is_resting(self):
        return self.type == SetType.REST.value or self.result == SetResult.DISCARDED.value

    @property
    def exercise_category_label(self):
        return _("Exercise")

    @property
    def exercise_category_value(self):
        if self.exercise_category is None:
            return "-"
        return EXERCISE_CATEGORY[self.exercise_category]["name"] if self.exercise_category in EXERCISE_CATEGORY else _("Unknown")

    @property
    def weight_label(self):
        return _("Weight")

    @property
    def weight_value(self):
        return SensorUtils.weight_to_str(self.weight)

    @property
    def repetitions_label(self):
        return _("Repetitions")

    @property
    def repetitions_value(self):
        return str(self.repetitions) if self.repetitions is not None else "-"

    @property
    def avghr_label(self):
        return _("Avg. Heart Rate")

    @property
    def avghr_value(self):
        return SensorUtils.hr_to_str(self.avghr)

    @property
    def maxhr_label(self):
        return _("Max. Heart Rate")

    @property
    def maxhr_value(self):
        return SensorUtils.hr_to_str(self.maxhr)

    @property
    def time_label(self):
        return _("Time")

    @property
    def time_value(self):
        return TimeUtils.ms_to_str(self.time, True)

    @property
    def calories_label(self):
        return _("Calories")

    @property
    def calories_value(self):
        return SensorUtils.calories_to_str(self.calories)

    @property
    def temperature_label(self):
        return _("Temperature")

    @property
    def temperature_value(self):
        return SensorUtils.temperature_to_str(self.temperature)

    @property
    def difficulty_label(self):
        return _("Difficulty")

    @property
    def difficulty_value(self):
        if self.difficulty is None:
            return "-"
        if int(self.difficulty) >= len(Set.DIFFICULTIES):
            return "-"
        return Set.DIFFICULTIES[int(self.difficulty)]

