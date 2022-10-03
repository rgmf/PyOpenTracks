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
import fitparse

from dataclasses import dataclass
from typing import List

from dateutil.tz import tzlocal

from pyopentracks.io.parser.fit.gain_loss_manager import GainLossManager
from pyopentracks.io.parser.records import Point


def dt_to_aware_locale_ms(dt: datetime):
    """From datetime to milliseconds taken time zone account.

    This function can be used to convert a UTC datetime to millis
    adding the local offset. So you'll have aware time zone datetime millis.
    """
    local_time_zone = tzlocal()
    offset_timedelta = local_time_zone.utcoffset(dt)
    return (dt.timestamp() + offset_timedelta.seconds) * 1000


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
        self._point.power = values["power"] if "power" in values else None
        self._point.temperature = values["temperature"] if "temperature" else None

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
