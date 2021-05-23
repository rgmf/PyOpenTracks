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


class TrackPoint:

    def __init__(self):
        self.location = {"longitude": None, "latitude": None}
        self.time = None
        self.speed = None
        self.elevation = None
        self.elevation_gain = None
        self.elevation_loss = None
        self.heart_rate = None
        self.cadence = None
        self.power = None

    @property
    def location_tuple(self):
        """Build and return a tuple object representing location."""
        return (float(self.location["latitude"]), float(self.location["longitude"]))

    @property
    def longitude(self):
        if self.location["longitude"]:
            return float(self.location["longitude"])
        return 0

    @property
    def latitude(self):
        if self.location["latitude"]:
            return float(self.location["latitude"])
        return 0
