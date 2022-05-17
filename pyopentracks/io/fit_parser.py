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
from pyopentracks.utils.utils import TimeUtils
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
        if not list(filter(lambda field_data: field_data.field and field_data.field.def_num == 0 and field_data.value and field_data.value == "activity", fields)):
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


class GainLossManager:
    """Smooth the elevation gain and loss noise."""

    # Ignore differences of DIFF_THRESHOLD between two consecutive altitudes.
    DIFF_THRESHOLD = 5
    # Elevation accumulation threshold to add gain or loss.
    ACCUM_THRESHOLD = 0.5

    def __init__(self):
        self._last_altitude = None

        self._gain_accum = 0
        self._gain = 0
        self._loss_accum = 0
        self._loss = 0

        self._total_gain = 0
        self._total_loss = 0

    def add(self, altitude):
        if self._last_altitude is None:
            self._last_altitude = altitude
            return

        if altitude is None:
            return

        diff = abs(self._last_altitude - altitude)

        if diff > GainLossManager.DIFF_THRESHOLD:
            self._last_altitude = altitude
            self._gain_accum = self._loss_accum = 0
            return

        if self._last_altitude < altitude:
            self._gain_accum += diff
            self._loss_accum = 0
            if self._gain_accum > GainLossManager.ACCUM_THRESHOLD:
                self._gain += self._gain_accum
                self._gain_accum = 0
        elif self._last_altitude > altitude:
            self._loss_accum += diff
            self._gain_accum = 0
            if self._loss_accum > GainLossManager.ACCUM_THRESHOLD:
                self._loss += self._loss_accum
                self._loss_accum = 0
        else:
            self._gain_accum = self._loss_accum = 0

        self._last_altitude = altitude

    def get_and_reset(self):
        gain, loss = self._gain, self._loss
        self._gain = self._loss = 0
        self._total_gain += gain
        self._total_loss += loss
        return gain, loss

class FitRecordMessage:
    """FIT record data message information."""

    # Read https://gis.stackexchange.com/questions/371656/garmin-fit-coodinate-system
    DIV_LAT_LON = pow(2, 32) / 360

    def __init__(self, record: fitparse.records.DataMessage, numsegment: int, manager: GainLossManager):
        values = record.get_values()
        self._numsegment = numsegment
        self._latitude = values["position_lat"] / FitRecordMessage.DIV_LAT_LON if "position_lat" in values else None
        self._longitude = values["position_long"] / FitRecordMessage.DIV_LAT_LON if "position_long" in values else None
        self._distance = values["distance"] if "distance" in values else None
        self._time_ms = TimeUtils.dt_to_aware_locale_ms(values["timestamp"]) if "timestamp" in values else None
        self._speed_mps = values["speed"] if "speed" in values else None
        self._altitude_m = values["altitude"] if "altitude" in values else None
        self._elevation_gain_m, self._elevation_loss_m = manager.get_and_reset()
        self._heart_rate_bpm = values["heart_rate"] if "heart_rate" in values else None
        self._cadence_rpm = values["cadence"] if "cadence" in values else None
        self._power_w = values["power"] if "power" in values else None
        self._temperature = values["temperature"] if "temperature" else None

    @property
    def track_point(self):
        return TrackPoint(
            None, self._numsegment, None, self._longitude, self._latitude, self._time_ms, self._speed_mps,
            self._altitude_m, self._elevation_gain_m, self._elevation_loss_m,
            self._heart_rate_bpm, self._cadence_rpm, self._power_w, self._temperature
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
        if hasattr(file_id, "manufacturer"):
            if hasattr(file_id, "product"):
                self._recorded_with = RecordedWith.from_device(file_id.manufacturer, file_id.product)
            else:
                self._recorded_with = RecordedWith.from_software(file_id.manufacturer)

        sport = FitSportMessage(fitfile)
        self._track = Track(
            None, None, sport.name, None, sport.category,
            None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None,
            self._recorded_with.id
        )
        self._track.category = sport.category

        stopped = False
        manager = GainLossManager()
        for mesg in [m for m in fitfile.messages if m.name in ("record", "event")]:
            if mesg.name == "record" and not stopped:
                fit_record_message = FitRecordMessage(mesg, self._num_segments, manager)
                self._add_track_point(fit_record_message.track_point)
                last_altitude = fit_record_message.track_point.altitude
                manager.add(last_altitude)
            elif mesg.name == "event":
                stopped = self._compute_mesg_event(mesg, stopped)

        super().close()

        track_stats = TrackStats()
        track_stats.compute(self._track_points)

        self._track.track_points = self._track_points
        self._track.add_track_stats(track_stats)
