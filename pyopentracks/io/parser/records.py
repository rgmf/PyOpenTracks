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
import time
from math import radians, sin, cos, asin, sqrt

from pyopentracks.io.parser.recorded_with import RecordedOptions, RecordedWith


class Record:
    """Class where parser will save the data extracted from files."""

    __slots__ = (
        "uuid", "name", "description", "time", "category", "recorded_with", "segments"
    )

    def __init__(self):
        self.uuid: str = None
        self.name: str = "PyOpenTracks"
        self.description: str = ""
        self.time: int = time.time() * 1000
        self.category: str = "Activity"
        self.recorded_with: RecordedWith = RecordedOptions[0]
        self.segments: list[Segment] = []

    def __repr__(self) -> str:
        return '<Record: uuid (%s) name (%s) description (%s) time (%d) category (%s) recorded_width (%s) segments (%d)>' % (
            self.uuid if self.uuid else "None", self.name, self.description, self.time,
            self.category, self.recorded_with.__repr__(), len(self.segments)
        )


class Segment:
    """A segment is a list of Point with an order.
    
    The first segment has the lower order and they are ordered.
    """

    __slots__ = ("points")

    def __init__(self):
        self.points: list[Point] = []

    def __repr__(self) -> str:
        return '<Segment: number of points (%d)>' % (len(self.points))


class Point:

    def __init__(self):
        self._latitude: float = None     # in decimals degree
        self._longitude: float = None    # in decimals degree
        self._distance: float = None     # in meters
        self._time: int = None           # in milliseconds (ms)
        self._speed: float = None        # in meters per second (mps)
        self._altitude: float = None     # in meters
        self._gain: float = None         # in meters
        self._loss: float = None         # in meters
        self._heart_rate: float = None   # in beats per minute (bpm)
        self._cadence: float = None      # in revolutions per minute (rpm)
        self._power: float = None        # in watt
        self._temperature: float = None  # in degrees

    @staticmethod
    def _is_float(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_int(value):
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
            
    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def distance(self):
        return self._distance

    @property
    def time(self):
        return self._time

    @property
    def speed(self):
        return self._speed

    @property
    def altitude(self):
        return self._altitude

    @property
    def gain(self):
        return self._gain

    @property
    def loss(self):
        return self._loss
    
    @property
    def heart_rate(self):
        return self._heart_rate

    @property
    def cadence(self):
        return self._cadence

    @property
    def power(self):
        return self._power

    @property
    def temperature(self):
        return self._temperature

    @latitude.setter
    def latitude(self, value):
        self._latitude = float(value) if Point._is_float(value) else None

    @longitude.setter
    def longitude(self, value):
        self._longitude = float(value) if Point._is_float(value) else None

    @distance.setter
    def distance(self, value):
        self._distance = float(value) if Point._is_float(value) else None

    @time.setter
    def time(self, value):
        self._time = int(value) if Point._is_int(value) else None

    @speed.setter
    def speed(self, value):
        self._speed = float(value) if Point._is_float(value) else None

    @altitude.setter
    def altitude(self, value):
        self._altitude = float(value) if Point._is_float(value) else None

    @gain.setter
    def gain(self, value):
        self._gain = float(value) if Point._is_float(value) else None

    @loss.setter
    def loss(self, value):
        self._loss = float(value) if Point._is_float(value) else None

    @heart_rate.setter
    def heart_rate(self, value):
        self._heart_rate = float(value) if Point._is_float(value) else None

    @cadence.setter
    def cadence(self, value):
        self._cadence = float(value) if Point._is_float(value) else None

    @power.setter
    def power(self, value):
        self._power = float(value) if Point._is_float(value) else None

    @temperature.setter
    def temperature(self, value):
        self._temperature = float(value) if Point._is_float(value) else None

    def is_location_valid(self):
        """Return True if this point has a valid location."""
        if not self.latitude or not self.longitude:
            return False

        try:
            if not self.latitude or not self.longitude:
                return False
            if (not (abs(self.latitude) <= 90 and abs(self.longitude) <= 180)):
                return False
        except Exception:
            return False
        return True

    def speed_between(self, from_point):
        """Returns the speed in mps between this point and to_point."""
        if not from_point or not self.is_location_valid() or not from_point.is_location_valid():
            return 0
        distance = self.distance_to(from_point)
        time = self.time - from_point.time
        return distance / (time / 1000.0)

    def distance_to(self, point):
        """Hervasian algorithm between this point and point.

        Return:
        Distance between the two points: from self to point in meters.
        """
        lon1, lat1, lon2, lat2 = map(radians, [self.longitude, self.latitude, point.longitude, point.latitude])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * 6371 * asin(sqrt(a)) * 1000

    def __repr__(self) -> str:
        return '<Point: latitude, longitude (%s, %s) distance (%s) time (%s) speed (%s) altitude (%s) gain, loss (%s, %s) heart_rate (%s) cadence (%s) power (%s) temperature (%s)>' % (
            self.latitude, self.longitude, self.distance, self.time, self.speed, self.altitude, self.gain, self.loss,
            self.heart_rate, self.cadence, self.power, self.temperature
        )
