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
from typing import List, Union
import fitparse
from pyopentracks.io.parser.fit.messages import FitSportMessage

from pyopentracks.io.parser.exceptions import FitParserException
from pyopentracks.io.parser.fit.gain_loss_manager import GainLossManager
from pyopentracks.io.parser.fit.messages import FitFileIdMessage, FitRecordMessage
from pyopentracks.io.parser.parser import Parser
from pyopentracks.io.parser.recorded_with import RecordedWith
from pyopentracks.io.parser.records import Point, Record, Segment


class Fit(Parser):
    """Interface with methods to implement for all FIT parsers."""

    def __init__(self, fitfile: fitparse.FitFile, file_id: FitFileIdMessage):
        super().__init__()
        self._fitfile = fitfile
        self._file_id = file_id


class FitActivity(Fit):
    """FIT parser for activity files."""

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

    def parse(self) -> Record:
        record = Record()
        record.recorded_with = RecordedWith.from_device(
            self._file_id.manufacturer, self._file_id.product
        )
        sport_message = FitSportMessage(self._fitfile)
        record.name = sport_message.name
        record.category = sport_message.category
        record.time = self._file_id.time_created_ms

        is_event_stopped = False
        is_moving = True
        gain_loss_manager = GainLossManager()
        segment_points: List[Point] = []
        last_point = None
        for mesg in [m for m in self._fitfile.messages if m.name in ("record", "event")]:
            if mesg.name == "record" and not is_event_stopped:
                point = FitRecordMessage(mesg, gain_loss_manager).point
                last_altitude = point.altitude
                gain_loss_manager.add(last_altitude)
                is_moving = self._is_moving(point, last_point)
                last_point = point
                segment_points.extend([point] if is_moving and point.is_location_valid() else [])
            elif mesg.name == "event":
                is_event_stopped = self._compute_mesg_event(mesg, is_event_stopped)

            if (is_event_stopped or not is_moving) and len(segment_points) > self._points_for_segment:
                segment = Segment()
                segment.points = segment_points
                record.segments.append(segment)
                segment_points = []

        if len(segment_points) > self._points_for_segment:
            segment = Segment()
            segment.points = segment_points
            record.segments.append(segment)

        return record


class FitSegment(Fit):
    """FIT parser for segments files."""
    
    def parse(self) -> Record:
        return super().parse()


FitTypes = {
    "activity": FitActivity,
    "segment": FitSegment,   
}


class PreParser:
    """Do a FIT file pre-parse."""

    def __init__(self, filename):
        self._filename = filename
        self._fitparse = None

    def parse(self) -> Union[FitActivity, FitSegment]:
        """Parse the FIT file and return the FIT parser depending on the file_id type.
        
        It checks if FileId message is supported and valid.

        Return:
            The parser needed to end parsing file.
        """
        fitfile = fitparse.FitFile(self._filename)
        messages = list(fitfile.get_messages("file_id"))
        file_id = messages[0] if len(messages) > 0 else None
        if not file_id:
            raise FitParserException(filename=self._filename, message="FIT file doesn't have a 'file_id' message")

        fields = [field_data for field_data in file_id.fields]
        type_list = list(filter(lambda field_data: field_data.name == "type", fields))
        if not type_list or len(type_list) != 1:
            raise FitParserException(filename=self._filename, message="type of the 'file_id' is wrong")

        field_data = type_list[0]
        if field_data.value not in FitTypes:
            raise FitParserException(filename=self._filename, message="FIT file type '" + str(field_data.value) + "' not supported")

        return FitTypes[field_data.value](fitfile, FitFileIdMessage(fields))
