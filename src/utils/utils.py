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

from datetime import datetime, timedelta


class DateTimeUtils:
    @staticmethod
    def ms_to_str(timestamp_ms: float) -> str:
        """From datetime millis to human readable string.

        Arguments:
        timestamp_ms -- timestamp in millis.

        Returns:
        An string representing the timestamp_ms in a human readable style.
        """
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime(
            "%a, %d %b %Y %H:%M:%S %Z"
        )


class TimeUtils:
    @staticmethod
    def ms_to_str(time_ms: float) -> str:
        """From time millis to human readable string.

        Arguments:
        time_ms -- time in millis.

        Returns:
        An string representing the time in HH:MM:SS format.
        """
        return str(timedelta(seconds=int(time_ms / 1000)))


class DistanceUtils:
    @staticmethod
    def m_to_str(distance_m: float) -> str:
        """From meters to human readable string.

        Arguments:
        distance_m -- distance in meters.

        Returns:
        An string representing the distance (in meters or km).
        """
        return (
            str(int(distance_m)) + " m" if distance_m < 1000
            else str(round(distance_m / 1000, 2)) + " km"
        )


class SpeedUtils:
    @staticmethod
    def mps_to_kph(speed_mps: float) -> str:
        """From meters per second to kilometeres per hour human readable.

        Arguments:
        speed_mps -- speed in meters per second.

        Returns:
        An string representing the speed_mps in a human readable format.
        """
        return str(round(speed_mps * 3.6, 1)) + " km/h"


class ElevationUtils:
    @staticmethod
    def elevation_to_str(elevation_m: float) -> str:
        """From float representation elevation to string elevation.

        Arguments:
        elevation_m -- elevation in meters.

        Returns:
        An string representing the elevation.
        """
        return (
            str(int(elevation_m)) + " m" if elevation_m is not None else "- m"
        )


class TypeActivityUtils:
    """Utilities for activities type.

    A set of utilities for get information, icons, etc, about activity's
    type.
    """

    _types = {
        "running": "icons/run_black_48dp.svg",
        "trail running": "icons/run_black_48dp.svg",

        "biking": "icons/bike_black_48dp.svg",
        "cycling": "icons/bike_black_48dp.svg",
        "road biking": "icons/bike_black_48dp.svg",
        "mountain biking": "icons/bike_black_48dp.svg",

        "walking": "icons/walk_black_48dp.svg",
        "trail walking": "icons/walk_black_48dp.svg",
        "hiking": "icons/walk_black_48dp.svg",
        "trail hiking": "icons/walk_black_48dp.svg",

        "driving": "icons/drive_car_black_48dp.svg",
    }

    @staticmethod
    def get_icon_resource(activity_type: str) -> str:
        """Gets and returns resource path icon for activity's type."""
        icon = TypeActivityUtils._types.get(activity_type)
        if icon is None:
            return "/es/rgmf/pyopentracks/icons/unknown_black_48dp.svg"

        return "/es/rgmf/pyopentracks/" + icon
