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
import datetime
from enum import Enum
import fitparse

from dataclasses import dataclass
from typing import List

from dateutil.tz import tzlocal
from pyopentracks.io.parser.fit.gain_loss_manager import GainLossManager
from pyopentracks.io.parser.records import Point, Set


def dt_to_aware_locale_ms(dt: datetime):
    """From datetime to milliseconds taken time zone account.

    This function can be used to convert a UTC datetime to millis
    adding the local offset. So you'll have aware time zone datetime millis.
    """
    local_time_zone = tzlocal()
    offset_timedelta = local_time_zone.utcoffset(dt)
    return (dt.timestamp() + offset_timedelta.seconds) * 1000


class SetType(Enum):
    REST = 0
    ACTIVE = 1


class SetResult(Enum):
    DISCARDED = 0
    COMPLETED = 1
    TRIED = 2


EXERCISE_CATEGORY = {
    0: {
        "value": 0,
        "value_name": "bench_press",
        "name": _("Bench press")
    },
    1: {
        "value": 1,
        "value_name": "calf_raise",
        "name": _("Calf raise")
    },
    2: {
        "value": 2,
        "value_name": "cardio",
        "name": _("Cardio")
    },
    3: {
        "value": 3,
        "value_name": "carry",
        "name": _("Carry")
    },
    4: {
        "value": 4,
        "value_name": "chop",
        "name": _("Chop")
    },
    5: {
        "value": 5,
        "value_name": "core",
        "name": _("Core")
    },
    6: {
        "value": 6,
        "value_name": "crunch",
        "name": _("Crunch")
    },
    7: {
        "value": 7,
        "value_name": "curl",
        "name": _("Curl")
    },
    8: {
        "value": 8,
        "value_name": "deadlift",
        "name": _("Deadlift")
    },
    9: {
        "value": 9,
        "value_name": "flye",
        "name": _("Flye")
    },
    10: {
        "value": 10,
        "value_name": "hip_raise",
        "name": _("Hip raise")
    },
    11: {
        "value": 11,
        "value_name": "hip_stability",
        "name": _("Hip stability")
    },
    12: {
        "value": 12,
        "value_name": "hip_swing",
        "name": _("Hip swing")
    },
    13: {
        "value": 13,
        "value_name": "hyperextension",
        "name": _("Hyperextension")
    },
    14: {
        "value": 14,
        "value_name": "lateral_raise",
        "name": _("Lateral raise")
    },
    15: {
        "value": 15,
        "value_name": "leg_curl",
        "name": _("Leg curl")
    },
    16: {
        "value": 16,
        "value_name": "leg_raise",
        "name": _("Leg raise")
    },
    17: {
        "value": 17,
        "value_name": "lunge",
        "name": _("Lunge")
    },
    18: {
        "value": 18,
        "value_name": "olympic_lift",
        "name": _("Olympic lift")
    },
    19: {
        "value": 19,
        "value_name": "plank",
        "name": _("Plank")
    },
    20: {
        "value": 20,
        "value_name": "plyo",
        "name": _("Plyo")
    },
    21: {
        "value": 21,
        "value_name": "pull_up",
        "name": _("Pull up")
    },
    22: {
        "value": 22,
        "value_name": "push_up",
        "name": _("Push up")
    },
    23: {
        "value": 23,
        "value_name": "row",
        "name": _("Row")
    },
    24: {
        "value": 24,
        "value_name": "shoulder_press",
        "name": _("Shoulder press")
    },
    25: {
        "value": 25,
        "value_name": "shoulder_stability",
        "name": _("Shoulder stability")
    },
    26: {
        "value": 26,
        "value_name": "shrug",
        "name": _("Shrug")
    },
    27: {
        "value": 27,
        "value_name": "sit_up",
        "name": _("Sit up")
    },
    28: {
        "value": 28,
        "value_name": "squat",
        "name": _("Squat")
    },
    29: {
        "value": 29,
        "value_name": "total_body",
        "name": _("Total body")
    },
    30: {
        "value": 30,
        "value_name": "triceps_extension",
        "name": _("Triceps extension")
    },
    31: {
        "value": 31,
        "value_name": "warm_up",
        "name": _("Warm up")
    },
    32: {
        "value": 32,
        "value_name": "run",
        "name": _("Run")
    },
    65524: {
        "value": 65524,
        "value_name": "unknown",
        "name": _("Unknown")
    }
}


@dataclass
class FitFileIdData:
    id: int
    name: str
    value: any


class FitFileIdMessage:
    """FIT file_id data message information.
    
    It represents a file_id FIT message (see SDK)
    """

    __slots__ = ("_fields")

    def __init__(self, fields):
        self._fields: List[FitFileIdData] = []
        for fd in list(filter(lambda i: i.field, fields)):
            self._fields.append(FitFileIdData(fd.field.def_num, fd.field.name, fd.value))

    @property
    def type(self):
        items = list(filter(lambda i: i.id == 0, self._fields))
        return items[0].value if items else None

    @property
    def manufacturer(self):
        items = list(filter(lambda i: i.id == 1, self._fields))
        return items[0].value if items else None

    @property
    def product(self):
        items = list(filter(lambda i: i.id == 2, self._fields))
        return items[0].value if items else None

    @property
    def serial_number(self):
        items = list(filter(lambda i: i.id == 3, self._fields))
        return items[0].value if items else None

    @property
    def time_created(self):
        items = list(filter(lambda i: i.id == 4, self._fields))
        return items[0].value if items else None

    @property
    def time_created_ms(self):
        time_created = self.time_created
        return dt_to_aware_locale_ms(time_created) if time_created else None


class FitSportMessage:
    """FIT sport data message information."""

    __slots__ = ("_name", "_category")

    def __init__(self, fitfile):
        self._name = "unknown"
        self._category = "unknown"

        messages = list(fitfile.get_messages("sport"))
        sport = messages[0] if len(messages) > 0 else None
        if sport:
            values = sport.get_values()
            self._name = values["name"] if "name" in values else "unknown"
            self._category = values["sport"] if "sport" in values else "unknown"

    @property
    def name(self):
        return self._name

    @property
    def category(self):
        return self._category

    def __repr__(self) -> str:
        return '<FitSportMessage: name (%s) category (%s)>' % (self.name, self.category)


class FitEventMessage:
    """FIT event data message information."""

    __slots__ = ("type", "timestamp")

    def __init__(self, mesg: fitparse.records.DataMessage):
        self.timestamp = None
        self.type = None

        values = mesg.get_values()
        if "event_type" in values and values["event_type"] == "stop_all":
            self.type = "stop_all"
            self.timestamp = dt_to_aware_locale_ms(values["timestamp"]) if "timestamp" in values else None


class FitRecordMessage:
    """FIT record data message information."""

    __slots__ = ("_point")

    # Read https://gis.stackexchange.com/questions/371656/garmin-fit-coodinate-system
    DIV_LAT_LON = pow(2, 32) / 360

    def __init__(self, record: fitparse.records.DataMessage, manager: GainLossManager):
        values = record.get_values()
        self._point = Point()

        self._point.latitude, self._point.longitude = self._lat_and_lon(values)
        self._point.distance = values["distance"] if "distance" in values else None
        self._point.time = dt_to_aware_locale_ms(values["timestamp"]) if "timestamp" in values else None
        self._point.speed = self._value(values, "enhanced_speed", "speed")
        self._point.altitude = self._value(values, "enhanced_altitude", "altitude")
        self._point.gain, self._point.loss = manager.get_and_reset()
        self._point.heart_rate = values["heart_rate"] if "heart_rate" in values else None
        self._point.cadence = values["cadence"] if "cadence" in values else None
        if self._point.cadence is not None:
            self._point.cadence += values["fractional_cadence"] if "fractional_cadence" in values else 0
        self._point.power = values["power"] if "power" in values else None
        self._point.temperature = values["temperature"] if "temperature" in values else None

    @property
    def point(self):
        return self._point

    @staticmethod
    def _lat_and_lon(values: dict):
        """Return latitude and longitude from values dictionary.

        Both latitude and longitude must be not None, otherwise it returns None for both.
        Also, it converts latitude and longitude from Garmin system to decimal degrees.
        """
        if "position_lat" not in values or "position_long" not in values:
            return None, None
        if values["position_lat"] is None or values["position_long"] is None:
            return None, None
        return (
            values["position_lat"] / FitRecordMessage.DIV_LAT_LON,
            values["position_long"] / FitRecordMessage.DIV_LAT_LON
        )

    @staticmethod
    def _value(values: dict, *keys):
        """Return the value for the first key found or None if any is found."""
        for key in keys:
            if key in values:
                return values[key]
        return None


class ClimbField(str, Enum):
    START = "unknown_9"
    END = "unknown_27"
    CALORIES = "unknown_28"
    AVGHR = "unknown_15"
    MAXHR = "unknown_16"
    DIFFICULTY = "unknown_70"
    ACTION = "unknown_0"        # climbing (9) or resting (10)
    RESULT = "unknown_71"       # completed (3) or try (2)
    DISCARDED = "unknown_80"    # discarded (0)


class FitClimbMessage:

    __slots__ = ("set")
    
    def __init__(self, mesg: fitparse.records.DataMessage):
        self.set = Set()
        for field_name, value in mesg.get_values().items():
            if field_name == ClimbField.START:
                self.set.start = value
            elif field_name == ClimbField.END:
                self.set.end = value
            elif field_name == ClimbField.CALORIES:
                self.set.calories = value
            elif field_name == ClimbField.AVGHR:
                self.set.avghr = value
            elif field_name == ClimbField.MAXHR:
                self.set.maxhr = value
            elif field_name == ClimbField.DIFFICULTY:
                self.set.difficulty = value
            elif field_name == ClimbField.ACTION:
                self.set.type = SetType.ACTIVE.value if value == 9 else SetType.REST.value
            elif field_name == ClimbField.RESULT and (value == 3 or value == 2):
                self.set.result = SetResult.COMPLETED.value if value == 3 else SetResult.TRIED.value
            elif field_name == ClimbField.DISCARDED and value == 0:
                self.set.result = SetResult.DISCARDED.value
        
    def __repr__(self) -> str:
        return "<FitClimbMessage: set (%s)>" % (self.set.__repr__())


class FitSetMessage:

    __slots__ = ("set")

    def __init__(self, mesg: fitparse.records.DataMessage):
        self.set = Set()
        duration_ms = None
        for field_name, value in mesg.get_values().items():
            if field_name == "start_time":
                self.set.start = dt_to_aware_locale_ms(value)
            elif field_name == "duration":
                duration_ms = value
            elif field_name == "repetitions":
                self.set.repetitions = value
            elif field_name == "category":
                self.set.exercise_category = None if value is None or len(value) == 0 or value[0] is None else value[0]
            elif field_name == "set_type":
                self.set.type = SetType.ACTIVE.value if value == "active" else SetType.REST.value
                self.set.result = SetResult.COMPLETED.value if value == 9 else None
        self.set.end = self.set.start + duration_ms if self.set.start is not None and duration_ms is not None else None

    def __repr__(self) -> str:
        return "<FitSetMessage: set (%s)>" % (self.set.__repr__())


class FitSessionMessage:

    __slots__ = (
        "sub_sport", "total_elapsed_time", "avg_heart_rate", "max_heart_rate",
        "avg_temperature", "max_temperature", "total_calories"
    )

    def __init__(self, mesg: fitparse.records.DataMessage):
        self.sub_sport = None
        self.total_elapsed_time = None
        self.avg_heart_rate = None
        self.max_heart_rate = None
        self.avg_temperature = None
        self.max_temperature = None
        self.total_calories = None

        for field_name, value in mesg.get_values().items():
            if field_name == "unknown_110":
                self.sub_sport = value
            elif field_name == "total_elapsed_time":
                self.total_elapsed_time = value
            elif field_name == "avg_heart_rate":
                self.avg_heart_rate = value
            elif field_name == "max_heart_rate":
                self.max_heart_rate = value
            elif field_name == "avg_temperature":
                self.avg_temperature = value
            elif field_name == "max_temperature":
                self.max_temperature = value
            elif field_name == "total_calories":
                self.total_calories = value

    def __repr__(self) -> str:
        return "<FitSessionMessage: sub_sport (%s) total_elapsed_time (%f) avg_heart_rate (%f) max_heart_rate (%f)" \
            "avg_temperature (%f) max_temperature (%f) total_calories (%f)>"  % (
                self.sub_sport if self.sub_sport is not None else "",
                self.total_elapsed_time if self.total_elapsed_time is not None else 0,
                self.avg_heart_rate if self.avg_heart_rate is not None else 0,
                self.max_heart_rate if self.max_heart_rate is not None else 0,
                self.avg_temperature if self.avg_temperature is not None else 0,
                self.max_temperature if self.max_temperature is not None else 0,
                self.total_calories if self.total_calories is not None else 0
            )

