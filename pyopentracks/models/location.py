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

import math


class Location:
    """A Location is an object with two values: latitude and longitude."""

    EARTH_RADIUS = 6371000 # in meters
    NORTH_DEGREES = 0
    EAST_DEGREES = 90
    SOUTH_DEGREES = 180
    WEST_DEGREES = 270

    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lon

    def calculate_derived_position(self, range, bearing):
        """Calculates a new Location derived from self.

        The new Location is range meters from this, in a direction indicated by bearing.

        Arguments:
        range   -- meters to go.
        bearing -- the direction to go (in degrees).

        Return:
        A new Location's object with the derived position.
        """
        latA = math.radians(self._lat)
        lonA = math.radians(self._lon)
        angularDistance = range / Location.EARTH_RADIUS
        trueCourse = math.radians(bearing)

        lat = math.asin(
            math.sin(latA) * math.cos(angularDistance) +
            math.cos(latA) * math.sin(angularDistance) * math.cos(trueCourse))

        dlon = math.atan2(
            math.sin(trueCourse) * math.sin(angularDistance) * math.cos(latA),
            math.cos(angularDistance) - math.sin(latA) * math.sin(lat))

        lon = ((lonA + dlon + math.pi) % (math.pi * 2)) - math.pi

        lat = math.degrees(lat)
        lon = math.degrees(lon)

        return Location(lat, lon)

    def bounding_box(self, radio):
        """Calculates a bounding box with the radio's meters indicated from this Location's object.

        Arguments:
        radio -- meters for the bounding box.

        Return:
        The BoundingBox's object.
        """
        return BoundingBox.from_location(self, radio)


class BoundingBox:
    """A bounding box are four locations: north, east, south and west from a location.

                            North's Location
                                   |
                                   | (radio)
                                   |
        West's Location _______(Location)________ East's Location
                                   |
                                   |
                                   |
                            South's Location
    """

    def __init__(self):
        self._location = None
        self._north = None
        self._east = None
        self._south = None
        self._west = None

    @property
    def location(self):
        return self._location

    @property
    def north(self):
        return self._north

    @property
    def east(self):
        return self._east

    @property
    def south(self):
        return self._south

    @property
    def west(self):
        return self._west

    @staticmethod
    def from_location(location: Location, radio: float):
        """Calculates a radio meters BoundingBox's object from the Location's location."""
        bounding_box = BoundingBox()
        bounding_box._location = location
        bounding_box._north = location.calculate_derived_position(radio, Location.NORTH_DEGREES)
        bounding_box._east = location.calculate_derived_position(radio, Location.EAST_DEGREES)
        bounding_box._south = location.calculate_derived_position(radio, Location.SOUTH_DEGREES)
        bounding_box._west = location.calculate_derived_position(radio, Location.WEST_DEGREES)
        return bounding_box