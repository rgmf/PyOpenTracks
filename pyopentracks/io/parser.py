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

from pyopentracks.utils import logging as pyot_logging


class Parser:
    """Generic class for parse files (import files).

    It contains the minimal logic to get all track's points and it guarantees
    all points are correct and it also handles segments, pauses, etc, in those
    points.

    All parsers have to extends it and they has to add track points calling
    _add_track_point method.
    """

    # Speed threshold for considering that there is not movement (in mps).
    # TODO This should be a setting's option ¿?
    AUTO_PAUSE_SPEED_THRESHOLD = 0.1
    # Number of segments needed for create a segment (otherwise are ignore).
    NUMBER_OF_POINTS_FOR_SEGMENT = 4

    def __init__(self):
        self._track = None
        self._current_segment_track_points = []
        self._num_segments = 0
        self._track_points = []
        self._new_segment = False

    def close(self):
        self._add_current_segment_points()

    def _add_track_point(self, track_point):
        # Check track_point is a good one.
        if track_point is None:
            return
        if not track_point.latitude or not track_point.longitude:
            return
        if not track_point.time_ms:
            return
        if not self._is_valid_location(
            track_point.latitude, track_point.longitude
        ):
            return

        # When a track_point is not moving and it's in the middle of a segment
        # or a new segment has to be created then finishes the current segment.
        if (
            (not self._is_moving(track_point.speed) and
             self._current_segment_track_points) or
            self._new_segment
        ):
            self._add_current_segment_points()
            self._new_segment = False

        # Add the track to the current segment.
        self._current_segment_track_points.append(track_point)

    def _add_current_segment_points(self):
        if len(self._current_segment_track_points) > Parser.NUMBER_OF_POINTS_FOR_SEGMENT:
            self._num_segments = self._num_segments + 1
            for i in self._current_segment_track_points:
                i.set_num_segment(self._num_segments)
            self._track_points.extend(self._current_segment_track_points)
        self._current_segment_track_points = []

    def _is_moving(self, speed):
        return speed and float(speed) >= Parser.AUTO_PAUSE_SPEED_THRESHOLD

    def _is_valid_location(self, lat, lon):
        try:
            if not lat or not lon:
                return False
            if (not (abs(lat) <= 90 and abs(lon) <= 180)):
                return False
        except Exception as e:
            pyot_logging.get_logger(__name__).exception(str(e))
            return False
        return True
