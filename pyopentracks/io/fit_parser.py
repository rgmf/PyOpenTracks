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
from dataclasses import dataclass

import fitparse

from pyopentracks.models.track import Track
from pyopentracks.models.track_point import TrackPoint

from pyopentracks.io.parser import Parser
from pyopentracks.io.result import RecordedWith
from pyopentracks.stats.track_stats import TrackStats


@dataclass
class FitFileIdData:
    id: int
    name: str
    value: any


class FitFileIdMessage:
    """FIT file_id data message information."""

    def __init__(self, fitfile):
        messages = list(fitfile.get_messages("file_id"))
        file_id = messages[0] if len(messages) > 0 else None
        if not file_id:
            raise Exception("FIT file doesn't have a 'file_id' message")

        fields = [field_data for field_data in file_id.fields]
        if not list(filter(lambda field_data: field_data.field and field_data.field.def_num == 0, fields)):
            raise Exception("It's not an 'activity' FIT file")

        self._data: List[FitFileIdData] = []
        for fd in list(filter(lambda i: i.field, fields)):
            self._data.append(FitFileIdData(fd.field.def_num, fd.field.name, fd.value))

    @property
    def time_created(self):
        items = list(filter(lambda i: i.id == 4, self._data))
        return items[0].value if items else None

    @property
    def serial_number(self):
        items = list(filter(lambda i: i.id == 3, self._data))
        return items[0].value if items else None

    @property
    def manufacturer(self):
        items = list(filter(lambda i: i.id == 1, self._data))
        return items[0].value if items else None

    @property
    def product(self):
        items = list(filter(lambda i: i.id == 2, self._data))
        return items[0].value if items else None


class FitSportMessage:
    """FIT sport data message information."""

    def __init__(self, fitfile):
        self._name = "unknown"

        messages = list(fitfile.get_messages("sport"))
        sport = messages[0] if len(messages) > 0 else None
        if sport:
            field_data = list(filter(lambda fd: fd.field and fd.field.def_num == 0, sport.fields))
            if field_data:
                self._name = field_data[0].value

    @property
    def category(self):
        return self._name


class FitRecordMessage:
    """FIT record data message information."""

    # Read https://gis.stackexchange.com/questions/371656/garmin-fit-coodinate-system
    DIV_LAT_LON = pow(2, 32) / 360

    def __init__(self, record: fitparse.records.DataMessage, numsegment: int, last_altitude: float):
        values = record.get_values()
        self._numsegment = numsegment
        self._latitude = values["position_lat"] / FitRecordMessage.DIV_LAT_LON if "position_lat" in values else None
        self._longitude = values["position_long"] / FitRecordMessage.DIV_LAT_LON if "position_long" in values else None
        self._distance = values["distance"] if "distance" in values else None
        self._time_ms = values["timestamp"].timestamp() * 1000 if "timestamp" in values else None
        self._speed_mps = values["speed"] if "speed" in values else None
        self._altitude_m = values["altitude"] if "altitude" in values else None
        self._elevation_gain_m = self._altitude_m - last_altitude if last_altitude is not None and self._altitude_m > last_altitude else 0
        self._elevation_loss_m = last_altitude - self._altitude_m if last_altitude is not None and self._altitude_m < last_altitude else 0
        self._heart_rate_bpm = values["heart_rate"] if "heart_rate" in values else None
        self._cadence_rpm = values["cadence"] if "cadence" in values else None
        self._power_w = values["power"] if "power" in values else None

    @property
    def track_point(self):
        return TrackPoint(
            None, self._numsegment, None, self._longitude, self._latitude, self._time_ms, self._speed_mps,
            self._altitude_m, self._elevation_gain_m, self._elevation_loss_m,
            self._heart_rate_bpm, self._cadence_rpm, self._power_w
        )


class FitParser(Parser):
    def __init__(self, filename_path):
        super().__init__()
        self._filename_path = filename_path

    def _compute_mesg_event(self, mesg: fitparse.records.DataMessage, stopped: bool) -> bool:
        fields = list(filter(lambda field_data: field_data.field and field_data.field.def_num == 1, mesg.fields))
        if not fields:
            return stopped

        field_data = fields[0]

        if field_data.value == "stop_all" and not stopped:
            self._new_segment = True
            return True

        if field_data.value == "start" and stopped:
            return False

        return stopped

    def parse(self):
        fitfile = fitparse.FitFile(self._filename_path)
        file_id = FitFileIdMessage(fitfile)
        if file_id.manufacturer == "garmin":
            self._recorded_with = RecordedWith.GARMIN

        sport = FitSportMessage(fitfile)
        self._track = Track(
            None, None, sport.category, None, sport.category,
            None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None
        )
        self._track.category = sport.category

        last_altitude = None
        stopped = False
        for mesg in [m for m in fitfile.messages if m.name in ("record", "event")]:
            if mesg.name == "record" and not stopped:
                fit_record_message = FitRecordMessage(mesg, self._num_segments, last_altitude)
                self._add_track_point(fit_record_message.track_point)
                last_altitude = fit_record_message.track_point.altitude
            elif mesg.name == "event":
                stopped = self._compute_mesg_event(mesg, stopped)

        super().close()

        track_stats = TrackStats()
        track_stats.compute(self._track_points)

        self._track.track_points = self._track_points
        self._track.add_track_stats(track_stats)
