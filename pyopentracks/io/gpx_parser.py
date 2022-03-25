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

from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import TrackPointUtils as tpu
from pyopentracks.models.track import Track
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.stats.track_stats import TrackStats
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

    def __init__(self):
        super().__init__()

        self._name = "PyOpenTracks"
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
                    self._recorded_with = RecordedWith.from_software("OpenTracks")
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
            self._new_track_point.latitude = attr["lat"] if "lat" in attr else None
            self._new_track_point.longitude = attr["lon"] if "lon" in attr else None

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
            None, None, None, None, None, self._recorded_with.id
        )
        self._track.track_points = self._track_points
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
            self._new_track_point.altitude = self._data
        elif tag == GpxParser.TAG_GAIN:
            self._new_track_point.elevation_gain = self._data
        elif tag == GpxParser.TAG_LOSS:
            self._new_track_point.elevation_loss = self._data
        elif tag == GpxParser.TAG_TIME:
            self._new_track_point.time_ms = tu.iso_to_ms(self._data)
        elif tag == GpxParser.TAG_SPEED:
            self._new_track_point.speed_mps = self._data
        elif tag == GpxParser.TAG_HR:
            self._new_track_point.heart_rate_bpm = self._data
        elif tag == GpxParser.TAG_CADENCE:
            self._new_track_point.cadence_rpm = self._data
        elif tag == GpxParser.TAG_TRKPT:
            if not self._new_track_point.time_ms:
                raise Exception("there are track points without time tag")
            if not self._new_track_point.speed_mps:
                self._new_track_point.speed_mps = tpu.speed(
                    self._last_track_point, self._new_track_point
                )
            self._add_track_point(self._new_track_point)
            self._last_track_point = self._new_track_point
            self._new_track_point = None
