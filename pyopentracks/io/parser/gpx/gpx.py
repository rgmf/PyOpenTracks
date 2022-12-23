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
from itertools import chain

from xml.etree.ElementTree import XMLParser
from pyopentracks.io.parser.parser import Parser
from pyopentracks.io.parser.recorded_with import RecordedWith
from pyopentracks.io.parser.records import Point, Record, Segment

from pyopentracks.utils.utils import TimeUtils, LocationUtils


class PreParser:
    """Do a GPX file pre-parse to build the Record's object.

    It uses the GpxParser class for parsing the GPX file.
    """

    def __init__(self, filename):
        self._filename = filename

    def parse(self) -> Record:
        parser = GpxParser()
        xmlparser = XMLParser(target=parser)
        with open(self._filename, "rb") as file:
            for data in file:
                xmlparser.feed(data)
            xmlparser.close()
        return parser.record


class GpxParser:
    """Parser for a GPX file.
    
    It loads all data from GPX to Track's object.
    """

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

        self._record = Record()
        self._segment = Segment()
        self._point = None

        self._tag = None
        self._data = ""

    @property
    def record(self):
        return self._record

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
                    self._record.recorded_with = RecordedWith.from_software("OpenTracks")
            self._tag = tag
        if tag == GpxParser.TAG_METADATA:
            self._tag = tag
        elif tag == GpxParser.TAG_TRK:
            self._tag = tag
        elif tag == GpxParser.TAG_TRKSEG:
            if self._segment.points:
                self._record.segments.append(self._segment)
            self._segment = Segment()
        elif tag == GpxParser.TAG_TRKPT:
            self._tag = tag
            self._point = Point()
            self._point.latitude = attr["lat"] if "lat" in attr else None
            self._point.longitude = attr["lon"] if "lon" in attr else None

    def end(self, tag):
        _, _, tag = tag.rpartition("}")

        if self._tag in (GpxParser.TAG_METADATA, GpxParser.TAG_TRK):
            self._end_tag_inside_metadata_trk(tag)
        elif self._tag == GpxParser.TAG_TRKPT:
            self._end_tag_inside_trkpt(tag)

    def data(self, d):
        self._data = self._data + d

    def close(self):
        if self._segment.points:
            self._record.segments.append(self._segment)
            self._record.start_time = self._record.segments[0].points[0].time
            self._record.end_time = self._record.segments[-1].points[-1].time

    def _end_tag_inside_metadata_trk(self, tag):
        """Compute the tag tag that is inside metadata or trk tag."""
        if tag == GpxParser.TAG_NAME:
            self._record.name = self._data
        elif tag == GpxParser.TAG_DESC:
            self._record.description = self._data
        elif tag == GpxParser.TAG_TYPE:
            self._record.category = self._data
        elif tag == GpxParser.TAG_TRACKID:
            self._record.uuid = self._data

    def _end_tag_inside_trkpt(self, tag):
        """Compute the tag tag that is inside trkpt tag."""
        if tag == GpxParser.TAG_ELEVATION:
            self._point.altitude = self._data
        elif tag == GpxParser.TAG_GAIN:
            self._point.gain = self._data
        elif tag == GpxParser.TAG_LOSS:
            self._point.loss = self._data
        elif tag == GpxParser.TAG_TIME:
            self._point.time = TimeUtils.iso_to_ms(self._data)
        elif tag == GpxParser.TAG_SPEED:
            self._point.speed = self._data
        elif tag == GpxParser.TAG_HR:
            self._point.heart_rate = self._data
        elif tag == GpxParser.TAG_CADENCE:
            self._point.cadence = self._data
        elif tag == GpxParser.TAG_TRKPT:
            self._segment.points.append(self._point)


class Gpx(Parser):
    """Generic GPX parser class."""

    def __init__(self, record: Record):
        super().__init__()
        self._record = record

    @property
    def record(self):
        return self._record


class GpxStandard(Gpx):
    """GPX parser for files with, at least, time."""

    def parse(self) -> Record:
        """Parse the record pre-parsed analyzing pauses/stops in the segments."""
        new_segments: list(Segment) = []
        for segment in self._record.segments:
            segment.points = list(filter(lambda p: self._is_point_valid(p), segment.points))
            new_segments.extend(self._compute_segment(segment))
        self._record.segments = new_segments
        return self._record

    def _compute_segment(self, segment: Segment) -> list[Segment]:
        """Split the segment into several if there are pauses/stops."""
        segments = []
        
        if not segment:
            return segments

        new_segment = Segment()
        initialPoint: Point = None
        for point in segment.points:
            if initialPoint is not None and not self._is_moving(point, initialPoint):
                segments.append(new_segment if new_segment.points else None)
                new_segment = Segment()
            else:
                new_segment.points.append(point)
            initialPoint = point

        if new_segment.points:
            segments.append(new_segment)

        return list(filter(lambda s: s and len(s.points) >= self._points_for_segment, segments))

    def _is_point_valid(self, point: Point) -> bool:
        """A Point is valid when it has a valid latitude/longitude and it has time."""
        if not point.is_location_valid():
            return False
        if point.time is None:
            return False
        return True


class GpxPath(Gpx):
    """GPX parser for files with only latitude and longitude points."""

    def parse(self) -> Record:
        points = list(chain(*[ s.points for s in self._record.segments ]))
        last_point = points.pop(0)
        last_point.distance = 0
        for point in points:
            point.distance = LocationUtils.distance_between(
                last_point.latitude, last_point.longitude,
                point.latitude, point.longitude
            )
            last_point = point
        return self._record


class GpxOpenTracks(GpxStandard):
    """GPX parser for GPX files recorded with OpenTracks.
    
    It is a GpxStandard with some features like gain and loss tags.
    """
    pass
