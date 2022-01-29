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

import threading

from xml.etree.ElementTree import XMLParser
from gi.repository import GLib, GObject

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import TrackPointUtils as tpu
from pyopentracks.models.track import Track
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.stats.track_stats import TrackStats
from pyopentracks.io.result import Result
from pyopentracks.io.result import RecordedWith
from pyopentracks.io.parser import Parser


class GpxParser(Parser):
    TAG_GPX = "gpx"
    
    TAG_METADATA = "metadata"
    TAG_TRK = "trk"
    TAG_NAME = "name"
    TAG_DESC = "desc"
    TAG_TYPE = "type"
    TAG_TRACKID = "trackid"

    TAG_TRKSEG = "trkseg"

    TAG_TRKPT = "trkpt"
    TAG_TIME = "time"
    TAG_SPEED = "speed"
    TAG_ELEVATION = "ele"
    TAG_GAIN = "gain"
    TAG_LOSS = "loss"
    TAG_HR = "hr"
    TAG_CADENCE = "cad"

    def __init__(self, filename_path):
        super().__init__()
        self._filename_path = filename_path
        self._recorded_with = RecordedWith.UNKNOWN

        self._name = _("No name")
        self._desc = None
        self._type = None
        self._uuid = None

        self._tag = None
        self._data = ""

        self._last_track_point = None
        self._new_track_point = None

    def start(self, tag, attr):
        _, _, tag = tag.rpartition("}")
        self._data = ""

        if tag == GpxParser.TAG_GPX:
            for k, v in attr.items():
                _, _, key = k.rpartition("}")
                if (
                    key == "schemaLocation" and
                    "http://opentracksapp.com/xmlschemas/v1" in v
                ):
                    self._recorded_with = RecordedWith.OPENTRACKS
            self._tag = tag
        if tag == GpxParser.TAG_METADATA:
            self._tag = tag
        elif tag == GpxParser.TAG_TRK:
            self._tag = tag
        elif tag == GpxParser.TAG_TRKSEG:
            self._new_segment = True
            self._last_track_point = None
        elif tag == GpxParser.TAG_TRKPT:
            self._tag = tag
            self._new_track_point = TrackPoint()
            self._new_track_point.set_latitude(
                attr["lat"] if "lat" in attr else None
            )
            self._new_track_point.set_longitude(
                attr["lon"] if "lon" in attr else None
            )

    def end(self, tag):
        _, _, tag = tag.rpartition("}")

        if self._tag in (GpxParser.TAG_METADATA, GpxParser.TAG_TRK):
            self._end_tag_inside_metadata_trk(tag)
        elif self._tag == GpxParser.TAG_TRKPT:
            self._end_tag_inside_trkpt(tag)

    def data(self, d):
        self._data = self._data + d

    def close(self):
        super().close()
        self._track = Track(
            None, self._uuid, self._name, self._desc, self._type,
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None
        )
        self._track.set_track_points(self._track_points)
        track_stats = TrackStats()
        track_stats.compute(self._track_points)
        self._track.add_track_stats(track_stats)

    def _end_tag_inside_metadata_trk(self, tag):
        """Compute the tag tag that is inside metadata or trk tag."""
        if tag == GpxParser.TAG_NAME:
            self._name = self._data
        elif tag == GpxParser.TAG_DESC:
            self._desc = self._data
        elif tag == GpxParser.TAG_TYPE:
            self._type = self._data
        elif tag == GpxParser.TAG_TRACKID:
            self._uuid = self._data

    def _end_tag_inside_trkpt(self, tag):
        """Compute the tag tag that is inside trkpt tag."""
        if tag == GpxParser.TAG_ELEVATION:
            self._new_track_point.set_altitude(self._data)
        elif tag == GpxParser.TAG_GAIN:
            self._new_track_point.set_elevation_gain(self._data)
        elif tag == GpxParser.TAG_LOSS:
            self._new_track_point.set_elevation_loss(self._data)
        elif tag == GpxParser.TAG_TIME:
            self._new_track_point.set_time(tu.iso_to_ms(self._data))
        elif tag == GpxParser.TAG_SPEED:
            self._new_track_point.set_speed(self._data)
        elif tag == GpxParser.TAG_HR:
            self._new_track_point.set_heart_rate(self._data)
        elif tag == GpxParser.TAG_CADENCE:
            self._new_track_point.set_cadence(self._data)
        elif tag == GpxParser.TAG_TRKPT:
            if not self._new_track_point.speed_mps:
                self._new_track_point.set_speed(
                    tpu.speed(self._last_track_point, self._new_track_point)
                )
            self._add_track_point(self._new_track_point)
            self._last_track_point = self._new_track_point
            self._new_track_point = None


class GpxParserHandler:
    """Handler the GPX parser task."""

    def parse(self, filename):
        try:
            gpx_parser = GpxParser(filename)
            parser = XMLParser(target=gpx_parser)
            with open(filename, 'rb') as file:
                for data in file:
                    parser.feed(data)
                parser.close()

            if not gpx_parser._track:
                raise Exception("empty track")

            tp = gpx_parser._track.track_points
            if not tp or len(tp) == 0:
                raise Exception("empty track")

            return Result(
                code=Result.OK,
                track=gpx_parser._track,
                filename=filename,
                recorded_with=gpx_parser._recorded_with
            )
        except Exception as error:
            message = f"Error parsing the file {filename}: {error}"
            pyot_logging.get_logger(__name__).exception(message)
            return Result(
                code=Result.ERROR,
                filename=filename,
                message=message
            )


class GpxParserHandlerInThread(GObject.GObject):
    """Handle the GPX parser task into a thread."""

    __gsignals__ = {
        "end-parse": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._filename = None
        self._callback = None

    def parse(self, filename, callback):
        """Parse the filename.
        Arguments:
        filename -- the filename to be parsed.
        callback -- a function that accept a dictionary with the
                    following keys:
                    - file: path's file.
                    - track: Track object or None if any error.
                    - error: message's error or None.
        """
        self._filename = filename
        self._callback = callback
        thread = threading.Thread(target=self._parse_in_thread)
        thread.daemon = True
        thread.start()

    def _parse_in_thread(self):
        try:
            gpx_parser = GpxParser(self._filename)
            parser = XMLParser(target=gpx_parser)
            with open(self._filename, 'rb') as file:
                for data in file:
                    parser.feed(data)
                parser.close()

            self.emit("end-parse")

            if not gpx_parser._track:
                raise Exception("empty track")

            tp = gpx_parser._track.track_points
            if not tp or len(tp) == 0:
                raise Exception("empty track")

            GLib.idle_add(
                self._callback,
                Result(
                    code=Result.OK,
                    filename=self._filename,
                    track=gpx_parser._track,
                    recorded_with=gpx_parser._recorded_with
                )
            )
        except Exception as error:
            message = f"Error parsing the file {self._filename}: {error}"
            pyot_logging.get_logger(__name__).exception(message)
            GLib.idle_add(
                self._callback,
                Result(
                    code=Result.ERROR,
                    filename=self._filename,
                    message=message
                )
            )
