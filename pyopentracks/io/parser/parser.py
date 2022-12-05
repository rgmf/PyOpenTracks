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
from abc import abstractmethod

from pyopentracks.io.parser.records import Point, Record


class Parser:

    def __init__(self):
        # Speed threshold for considering that there is not movement (in mps).
        self._speed_threshold_auto_pause = 0.1
        # Number of points needed for create a segment (otherwise are ignore).
        self._points_for_segment = 4

    def set_speed_threshold(self, speed):
        self._speed_threshold_auto_pause = speed
        return self

    def set_points_for_segment(self, n_points):
        self._points_for_segment = n_points
        return self

    @abstractmethod
    def parse(self) -> Record:
        pass

    def _is_moving(self, point: Point, initial: Point=None):
        """Return True if point is a moving one. Otherwise it returns False.
        
        A point is a moving one if:
        1. it has speed and it is greater or equal than the threshold or
        2. there is an previous point (initial) and computed speed between these two 
           points are greater or equal tha the threshold.
        """
        speed = point.speed if point.speed is not None else point.speed_between(initial)
        return speed and speed >= self._speed_threshold_auto_pause
