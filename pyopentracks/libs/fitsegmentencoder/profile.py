"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>.

This file is part of fit-segment-encoder.

fit-segment-encoder is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

fit-segment-encoder is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fit-segment-encoder. If not, see <https://www.gnu.org/licenses/>.
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from struct import pack
from typing import List

from .definitions import FIT_BASE_TYPES

# According to the SDK date_time type is computed counting the seconds since this datetime: UTC 00:00 Dec 31 1989
date_time_seconds_since = datetime(1989, 12, 31, 0, 0, 0).timestamp()


@dataclass
class Type:
    number: int
    size: int
    format: str

    def is_string(self):
        return self.number == FIT_BASE_TYPES["string"]


@dataclass
class Field:
    number: int
    name: str
    type: Type
    value: [int, bytes]
    scale: int = None
    offset: int = None

    def is_string(self):
        return self.type.is_string()

    def has_scale(self):
        return self.scale is not None and isinstance(self.value, int)

    def has_offset(self):
        return self.offset is not None and isinstance(self.value, int)


@dataclass
class Message:
    name: str
    number: int
    fields: List[Field]

    def set_field_value(self, name: str, value: any):
        fields = list(filter(lambda f: f.name == name, self.fields))
        if not fields:
            return
        field = fields[0]
        field.value = value
        if field.type.is_string():
            field.type.size = len(value)
            field.type.format = str(len(value)) + "s"
        if field.has_offset():
            field.value += field.offset
        if field.has_scale():
            field.value *= field.scale


class Crc(object):
    """FIT file CRC computation."""

    CRC_TABLE = (
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    )

    FMT = "H"

    def __init__(self, value=0, byte_arr=None):
        self.value = value
        if byte_arr:
            self.update(byte_arr)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.value or "-")

    def __str__(self):
        return self.format(self.value)

    def update(self, byte_arr):
        """Read bytes and update the CRC computed."""
        if byte_arr:
            self.value = self.calculate(byte_arr, self.value)

    @staticmethod
    def format(value):
        """Format CRC value to string."""
        return "0x%04X" % value

    @classmethod
    def calculate(cls, byte_arr, crc=0):
        """Compute CRC for input bytes."""
        for byte in bytearray(byte_arr):
            # Taken verbatim from FIT SDK docs
            tmp = cls.CRC_TABLE[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ cls.CRC_TABLE[byte & 0xF]

            tmp = cls.CRC_TABLE[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ cls.CRC_TABLE[(byte >> 4) & 0xF]
        return crc


def get_message(global_msg: str):
    if global_msg not in FIT_MESSAGES:
        raise Exception(f"{global_msg} is not a supported message")
    return FIT_MESSAGES[global_msg]


class Record:
    """Contains definition and data message of the message global_msg."""
    def __init__(self, message: Message, architecture: int = 0):
        endian = "<" if architecture == 0 else ">"
        fields = list(filter(lambda f: f.value is not None, message.fields))
        number_of_fields = len(fields)

        self._definition_header = pack(endian + "B", 64)
        self._definition_message = pack(endian + "BBHB", 0, architecture, message.number, number_of_fields)
        self._definition_fields = [pack(endian + "BBB", f.number, f.type.size, f.type.number) for f in fields]

        self._data_header = pack(endian + "B", 0)
        self._data_messages = [pack(endian + f.type.format, f.value) for f in fields]

    @property
    def bytes(self):
        return (
            self._definition_header + self._definition_message +
            reduce(lambda x, y: x + y, self._definition_fields) +
            self._data_header + reduce(lambda x, y: x + y, self._data_messages)
        )


FIT_MESSAGES = {
    "file_id": Message(
        name="file_id",
        number=0,
        fields=[
            Field(
                number=0,
                name="type",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=34  # segment
            ),
            Field(
                number=1,
                name="manufacturer",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=2,
                name="product",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=3,
                name="serial_number",
                type=Type(FIT_BASE_TYPES["uint32z"], 4, "I"),
                value=None
            ),
            Field(
                number=4,
                name="time_created",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=int(datetime.now().timestamp() - date_time_seconds_since)
            ),
        ]
    ),
    "file_creator": Message(
        name="file_creator",
        number=49,
        fields=[
            Field(
                number=0,
                name="software_version",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=0
            ),
            Field(
                number=1,
                name="hardware_version",
                type=Type(FIT_BASE_TYPES["uint8"], 1, "B"),
                value=0
            ),
        ]
    ),
    "segment_id": Message(
        name="segment_id",
        number=148,
        fields=[
            Field(
                number=0,
                name="name",
                type=Type(FIT_BASE_TYPES["string"], 7, "7s"),
                value=b"Segment"  # default's name
            ),
            Field(
                number=1,
                name="uuid",
                type=Type(FIT_BASE_TYPES["string"], 36, "36s"),
                value=str(uuid.uuid4()).encode(encoding="utf-8")
            ),
            Field(
                number=2,
                name="sport",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=None
            ),
            Field(
                number=3,
                name="enabled",
                type=Type(FIT_BASE_TYPES["byte"], 1, "B"),
                value=1  # True
            ),
        ]
    ),
    "segment_leaderboard_entry": Message(
        name="segment_leaderboard_entry",
        number=149,
        fields=[
            Field(
                number=254,
                name="message_index",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=0  # default's message_index value
            ),
            Field(
                number=0,
                name="name",
                type=Type(FIT_BASE_TYPES["string"], 11, "11s"),
                value=b"Leaderboard"  # default's name
            ),
            Field(
                number=1,
                name="type",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=None
            ),
            Field(
                number=2,
                name="group_primary_key",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None
            ),
            Field(
                number=3,
                name="activity_id",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None
            ),
            Field(
                number=4,
                name="segment_time",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None,
                scale=1000
            ),
            Field(
                number=5,
                name="activity_id_string",
                type=Type(FIT_BASE_TYPES["string"], 1, "s"),
                value=None
            ),
        ]
    ),
    "segment_lap": Message(
        name="segment_lap",
        number=142,
        fields=[
            Field(
                number=254,
                name="message_index",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=0  # default's message_index value
            ),
            Field(
                number=253,
                name="timestamp",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None
            ),
            Field(
                number=0,
                name="event",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=None
            ),
            Field(
                number=1,
                name="event_type",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=None
            ),
            Field(
                number=2,
                name="start_time",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=int(datetime.now().timestamp() - date_time_seconds_since)
            ),
            Field(
                number=3,
                name="start_position_lat",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=None
            ),
            Field(
                number=4,
                name="start_position_long",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=None
            ),
            Field(
                number=5,
                name="end_position_lat",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=None
            ),
            Field(
                number=6,
                name="end_position_long",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=None
            ),
            Field(
                number=7,
                name="total_elapsed_time",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=0,
                scale=1000
            ),
            Field(
                number=8,
                name="total_timer_time",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None,
                scale=1000
            ),
            Field(
                number=9,
                name="total_distance",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None,
                scale=100
            ),
            Field(
                number=10,
                name="total_strokes",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None
            ),
            Field(
                number=11,
                name="total_calories",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=12,
                name="total_fat_calories",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=13,
                name="avg_speed",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None,
                scale=1000
            ),
            Field(
                number=14,
                name="max_speed",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None,
                scale=1000
            ),
            Field(
                number=15,
                name="avg_heart_rate",
                type=Type(FIT_BASE_TYPES["uint8"], 1, "B"),
                value=None
            ),
            Field(
                number=16,
                name="max_heart_rate",
                type=Type(FIT_BASE_TYPES["uint8"], 1, "B"),
                value=None
            ),
            Field(
                number=17,
                name="avg_cadence",
                type=Type(FIT_BASE_TYPES["uint8"], 1, "B"),
                value=None
            ),
            Field(
                number=18,
                name="max_cadence",
                type=Type(FIT_BASE_TYPES["uint8"], 1, "B"),
                value=None
            ),
            Field(
                number=19,
                name="avg_power",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=20,
                name="max_power",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=21,
                name="total_ascent",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=22,
                name="total_descent",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=None
            ),
            Field(
                number=23,
                name="sport",
                type=Type(FIT_BASE_TYPES["enum"], 1, "B"),
                value=None
            ),
        ]
    ),
    "segment_point": Message(
        name="segment_point",
        number=150,
        fields=[
            Field(
                number=254,
                name="message_index",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=0  # default's message_index value
            ),
            Field(
                number=1,
                name="position_lat",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=0
            ),
            Field(
                number=2,
                name="position_long",
                type=Type(FIT_BASE_TYPES["sint32"], 4, "i"),
                value=0
            ),
            Field(
                number=3,
                name="distance",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=0,
                scale=100
            ),
            Field(
                number=4,
                name="altitude",
                type=Type(FIT_BASE_TYPES["uint16"], 2, "H"),
                value=0,
                scale=5,
                offset=500
            ),
            Field(
                number=5,
                name="leader_time",
                type=Type(FIT_BASE_TYPES["uint32"], 4, "I"),
                value=None,
                scale=1000
            ),
        ]
    ),
}
