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
from struct import pack
from typing import List

from .definitions import MANUFACTURER, PRODUCT, SEGMENT_LEADERBOARD_TYPE
from .profile import Record, get_message, Crc


@dataclass
class SegmentPoint:
    message_index: int
    latitude: int
    longitude: int
    distance: int
    altitude: int
    best_time: int = None
    leader_time: int = None


class AscentDescentManager:
    """Smooth the elevation ascent and descent noise."""

    # Ignore differences of DIFF_THRESHOLD between two consecutive altitudes.
    DIFF_THRESHOLD = 5
    # Elevation accumulation threshold to add ascent or descent.
    ACCUM_THRESHOLD = 0.5

    def __init__(self):
        self._last_altitude = None

        self._ascent_accum: int = 0
        self._ascent: int = 0
        self._descent_accum: int = 0
        self._descent: int = 0

        self._total_ascent: int = 0
        self._total_descent: int = 0

    def add(self, altitude):
        if self._last_altitude is None:
            self._last_altitude = altitude
            return

        if altitude is None:
            return

        diff = abs(self._last_altitude - altitude)

        if diff > AscentDescentManager.DIFF_THRESHOLD:
            self._last_altitude = altitude
            self._ascent_accum = self._descent_accum = 0
            return

        if self._last_altitude < altitude:
            self._ascent_accum += diff
            self._descent_accum = 0
            if self._ascent_accum > AscentDescentManager.ACCUM_THRESHOLD:
                self._ascent += self._ascent_accum
                self._ascent_accum = 0
        elif self._last_altitude > altitude:
            self._descent_accum += diff
            self._ascent_accum = 0
            if self._descent_accum > AscentDescentManager.ACCUM_THRESHOLD:
                self._descent += self._descent_accum
                self._descent_accum = 0
        else:
            self._ascent_accum = self._descent_accum = 0

        self._last_altitude = altitude

    def get_and_reset(self):
        ascent, descent = self._ascent, self._descent
        self._ascent = self._descent = 0
        self._total_ascent += ascent
        self._total_descent += descent
        return ascent, descent


@dataclass
class SegmentLeader:
    type: int
    segment_time: int = None
    name: str = None
    activity_id: int = None
    activity_id_string: str = None
    group_primary_key: int = None


@dataclass
class SegmentBytes:
    file_id: bytes = b""
    file_creator: bytes = b""
    segment_id: bytes = b""
    segment_leaderboard_entry: bytes = b""
    segment_lap: bytes = b""
    segment_point: bytes = b""

    def get(self):
        return (
            self.file_id +
            self.file_creator +
            self.segment_id +
            self.segment_leaderboard_entry +
            self.segment_lap +
            self.segment_point
        )


class FitSegmentEncoder:
    """Class to be used to encode segment FIT files.

    Segment FIT files will contain:
    - One file_id message with type=segment, time_created, manufacturer, product and other fields.
    - One file_creator.
    - One segment_id message with name, sport and enabled=True.
    - One segment_leaderboard_entry messages with information about personal_best data, only if there are leader_time
      in segment_point messages.
    - One segment_lap message.
    - Several segment_point messages.
    """

    def __init__(self, name: str, sport: int, segment_points: List[SegmentPoint]):
        self._bytes = SegmentBytes()

        self._name = name
        self._sport = sport
        self._segment_points = segment_points

        self._leaders: List[SegmentLeader] = []
        self._segment_pr_leader = SegmentLeader(type=SEGMENT_LEADERBOARD_TYPE["personal_best"], name="PR")

        manager = AscentDescentManager()

        self._encode_message_file_id()
        self._encode_message_file_creator()
        self._encode_message_segment_id()
        for idx, sp in enumerate(self._segment_points):
            manager.add(sp.altitude)
            self._encode_message_segment_point(sp, idx)
        self._encode_message_segment_lap(manager)
        self._encode_message_segment_leaderboard_entry()

    def _encode_message_file_id(self):
        """Encode the file_id message of type=segment."""
        message = get_message("file_id")
        message.set_field_value("manufacturer", MANUFACTURER["garmin"])
        message.set_field_value("product", PRODUCT["edge_530"])
        record = Record(message)
        self._bytes.file_id = record.bytes

    def _encode_message_file_creator(self):
        """Encode the file_creator message."""
        record = Record(get_message("file_creator"))
        self._bytes.file_creator = record.bytes

    def _encode_message_segment_id(self):
        message = get_message("segment_id")
        message.set_field_value("uuid", str(uuid.uuid4()).encode(encoding="utf-8"))
        message.set_field_value("name", (self._name + "\0").encode(encoding="utf-8"))
        message.set_field_value("sport", self._sport)
        record = Record(message)
        self._bytes.segment_id = record.bytes

    def _encode_message_segment_lap(self, manager: AscentDescentManager):
        ascent, descent = manager.get_and_reset()

        message = get_message("segment_lap")
        message.set_field_value("message_index", 0)
        message.set_field_value("start_position_lat", self._segment_points[0].latitude)
        message.set_field_value("start_position_long", self._segment_points[0].longitude)
        message.set_field_value("end_position_lat", self._segment_points[-1].latitude)
        message.set_field_value("end_position_long", self._segment_points[-1].longitude)
        message.set_field_value("total_distance", self._segment_points[-1].distance)
        message.set_field_value("total_ascent", ascent)
        message.set_field_value("total_descent", descent)
        message.set_field_value("sport", self._sport)
        record = Record(message)
        self._bytes.segment_lap = record.bytes

    def _encode_message_segment_point(self, sp: SegmentPoint, idx: int):
        self._segment_pr_leader.segment_time = sp.leader_time

        message = get_message("segment_point")
        message.set_field_value("message_index", idx)
        message.set_field_value("position_lat", sp.latitude)
        message.set_field_value("position_long", sp.longitude)
        message.set_field_value("distance", sp.distance)
        message.set_field_value("altitude", sp.altitude)
        message.set_field_value("leader_time", sp.leader_time)
        record = Record(message)
        self._bytes.segment_point += record.bytes

    @property
    def _data_bytes(self):
        return self._bytes.get()

    def _encode_message_segment_leaderboard_entry(self):
        if self._segment_pr_leader.segment_time is None:
            return
        leader = self._segment_pr_leader
        message = get_message("segment_leaderboard_entry")
        message.set_field_value("message_index", len(self._leaders))
        message.set_field_value("type", leader.type)
        message.set_field_value("segment_time", leader.segment_time)
        if leader.name:
            message.set_field_value("name", (leader.name + "\0").encode(encoding="utf-8"))
        if leader.activity_id:
            message.set_field_value("activity_id", leader.activity_id)
        if leader.activity_id_string:
            message.set_field_value("activity_id_string", leader.activity_id_string.encode(encoding="utf-8"))
        if leader.group_primary_key:
            message.set_field_value("group_primary_key", leader.group_primary_key)
        record = Record(message)

        self._leaders.append(leader)

        self._bytes.segment_leaderboard_entry += record.bytes

    def end_and_get(self):
        """Finish FIT segment binary encoded data and return it.

        The return value is ready for saving into a binary file.
        """
        data_size = len(self._data_bytes)

        header = pack("BBHI", 14, 1, 1, data_size)
        header += b".FIT"
        crc_header = Crc()
        crc_header.update(header)
        header += pack("H", crc_header.value)

        crc_file = Crc()
        crc_file.update(self._data_bytes)
        crc_pack = pack("H", crc_file.value)

        return header + self._data_bytes + crc_pack
