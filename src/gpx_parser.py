"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>

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

from .track_stats import TrackStats, Track


class GpxParser:
    TAG_METADATA = "metadata"
    TAG_TRK = "trk"
    TAG_NAME = "name"
    TAG_DESC = "desc"
    TAG_TYPE = "type"

    TAG_TRKSEG = "trkseg"

    TAG_TRKPT = "trkpt"
    TAG_TIME = "time"
    TAG_SPEED = "speed"
    TAG_ELEVATION = "ele"
    TAG_GAIN = "gain"
    TAG_LOSS = "loss"

    def __init__(self):
        self._name = None
        self._desc = None
        self._type = None

        self._tag = None
        self._data = ""

        self._segment = 0

        self._new_trk_point = None
        self._track = Track()
        self._track_stats = TrackStats()

    def start(self, tag, attr):
        _, _, tag = tag.rpartition("}")
        self._data = ""

        if tag == GpxParser.TAG_METADATA:
            self._tag = tag
        elif tag == GpxParser.TAG_TRK:
            self._tag = tag
        elif tag == GpxParser.TAG_TRKPT:
            self._tag = tag
            self._new_trk_point = {
                "location": {
                    "latitude": attr["lat"] if "lat" in attr else None,
                    "longitude": attr["lon"] if "lon" in attr else None
                },
                "elevation": None,
                "elevation_gain": None,
                "elevation_loss": None,
                "time": None,
                "speed": None,
                "cadence": None,
                "heart_rate": None,
                "power": None,
            }

    def end(self, tag):
        _, _, tag = tag.rpartition("}")

        if self._tag in (GpxParser.TAG_METADATA, GpxParser.TAG_TRK):
            self._end_tag_inside_metadata_trk(tag)
        elif self._tag == GpxParser.TAG_TRKSEG:
            self._segment = self._segment + 1
        elif self._tag == GpxParser.TAG_TRKPT:
            self._end_tag_inside_trkpt(tag)

    def data(self, d):
        self._data = self._data + d

    def close(self):
        self._track._name = self._name
        self._track._desc = self._desc
        self._track._type = self._type
        self._track._track_stats = self._track_stats

    def _end_tag_inside_metadata_trk(self, tag):
        """Compute the tag tag that is inside metadata or trk tag."""
        if tag == GpxParser.TAG_NAME:
            self._name = self._data
        elif tag == GpxParser.TAG_DESC:
            self._desc = self._data
        elif tag == GpxParser.TAG_TYPE:
            self._type = self._data

    def _end_tag_inside_trkpt(self, tag):
        """Compute the tag tag that is inside trkpt tag."""
        if tag == GpxParser.TAG_ELEVATION:
            self._new_trk_point["elevation"] = self._data
        elif tag == GpxParser.TAG_GAIN:
            self._new_trk_point["elevation_gain"] = self._data
        elif tag == GpxParser.TAG_LOSS:
            self._new_trk_point["elevation_loss"] = self._data
        elif tag == GpxParser.TAG_TIME:
            self._new_trk_point["time"] = self._data
        elif tag == GpxParser.TAG_SPEED:
            self._new_trk_point["speed"] = self._data
        elif tag == GpxParser.TAG_TRKPT:
            self._track_stats.new_track_point(
                self._new_trk_point, self._segment
            )
            self._new_trk_point = None


class GpxParserHandle(GObject.GObject):
    """Handle the GPX parser task into a thread."""

    __gsignals__ = {
        'end-parse': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._filename = None
        self._callback = None

    def parse(self, filename, callback):
        """Parse the filename.
        Arguments:
        filename -- the filename to be parsed.
        callback -- a function that accept TrackStats object to be
                    called when parsing is finished. It's a function
                    used to get the result of the parsing.
        """
        self._filename = filename
        self._callback = callback
        thread = threading.Thread(target=self._parse_in_thread)
        thread.daemon = True
        thread.start()

    def _parse_in_thread(self):
        gpx_parser = GpxParser()
        parser = XMLParser(target=gpx_parser)
        with open(self._filename, 'rb') as file:
            for data in file:
                parser.feed(data)
        parser.close()
        self.emit("end-parse")
        GLib.idle_add(self._callback, gpx_parser._track)

# gpx_parser = GpxParser()
# parser = XMLParser(target=gpx_parser)
# with open('934.gpx', 'rb') as file:
#     for data in file:
#         parser.feed(data)
# parser.close()


# print(gpx_parser._name, gpx_parser._desc, gpx_parser._type)
# print(
#     "Track stats times:",
#     gpx_parser._track_stats._start_time_ms,
#     gpx_parser._track_stats._end_time_ms,
#     gpx_parser._track_stats._total_time_ms,
#     gpx_parser._track_stats._moving_time_ms
# )
# from datetime import datetime
# print(
#     "Track stats times:",
#     datetime.fromtimestamp(gpx_parser._track_stats._start_time_ms / 1000),
#     datetime.fromtimestamp(gpx_parser._track_stats._end_time_ms / 1000),
#     gpx_parser._track_stats._total_time_ms / 1000 / 60,
#     gpx_parser._track_stats._moving_time_ms / 1000 / 60,
#     gpx_parser._track_stats._total_distance_m * 1000,
#     gpx_parser._track_stats._avg_speed_mps * 3.6,
#     gpx_parser._track_stats._max_speed_mps * 3.6
# )
