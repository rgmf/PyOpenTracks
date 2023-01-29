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
import os.path
import time

from gi.repository import GdkPixbuf

from collections import namedtuple
from math import radians, sin, cos, asin, sqrt
from typing import List

from dateutil.parser import isoparse
from dateutil.tz import tzlocal
from datetime import datetime, timedelta, date, timezone
from calendar import monthrange
from locale import setlocale, LC_ALL

from pyopentracks.models.location import Location


class DateTimeUtils:
    @staticmethod
    def begin_of_day(year: int, month: int, day: int):
        return datetime(year, month, day, 0, 0, 0).timestamp() * 1000

    @staticmethod
    def end_of_day(year: int, month: int, day: int):
        return datetime(year, month, day, 23, 59, 59).timestamp() * 1000

    @staticmethod
    def ms_to_str(timestamp_ms: float, short=False) -> str:
        """From datetime millis to human readable string.

        Arguments:
        timestamp_ms -- timestamp in millis.
        short        -- (optional) for a short version.

        Returns:
        An string representing the timestamp_ms in a human readable style.
        """
        if not timestamp_ms:
            return "-"
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime(
            "%a, %d %b %Y %H:%M:%S" if not short else "%d %b %Y"
        )

    @staticmethod
    def first_day_ms(year: int, month: int) -> int:
        """Return the millis of the first day of the year/month."""
        return datetime(year, month, 1, 0, 0, 0).timestamp() * 1000

    @staticmethod
    def last_day_ms(year: int, month: int) -> int:
        """Return the millis of the last day of the year/month."""
        weekday, num_days = monthrange(year, month)
        return datetime(year, month, num_days, 23, 59, 59).timestamp() * 1000

    @staticmethod
    def date_from_timestamp(timestamp: int) -> namedtuple:
        dt = datetime.fromtimestamp(timestamp / 1000)
        TodayResult = namedtuple("TodayResult", "year month day")
        return TodayResult(dt.year, dt.month, dt.day)

class DateUtils:
    @staticmethod
    def get_months():
        """Return the list of months names."""
        setlocale(LC_ALL, '')
        return [
            datetime.strptime(str(i), "%m").strftime("%B")
            for i in range(1, 13)
        ]

    @staticmethod
    def get_month_name(month: int) -> str:
        """Return the name of the month.

        Arguments:
        month -- number of month from 1 to 12.

        Return:
        Month's name or January if month is out of 1 - 12 range.
        """
        if not isinstance(month, int) or not 1 <= month <= 12:
            return DateUtils.get_months()[0]
        return DateUtils.get_months()[month - 1]

    @staticmethod
    def get_today():
        """Return year, month and day of today."""
        t = date.today()
        TodayResult = namedtuple("TodayResult", "year month day")
        return TodayResult(t.year, t.month, t.day)


class TimeUtils:
    @staticmethod
    def utc_offset_str() -> str:
        """Return and string with the offset of the local timezone from the computer.

        Examples:
            +02:00
            -04:00
        """
        ts = time.time()
        utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()
        hours = int(utc_offset / 3600)
        minutes = int((utc_offset % 3600) / 60)
        return f"{hours:+03d}:{minutes:02d}"

    @staticmethod
    def ms_to_str(time_ms: float, shorten=False) -> str:
        """From time millis to human readable string.

        Arguments:
        time_ms -- time in millis.
        shorten -- (optional) full (False) or shorten (True) version.

        Returns:
        An string representing the time in HH:MM:SS format when shorten is False.
        An string representing the time in HHh \n MMm format when shorten is True.
        """
        if not time_ms:
            return "-"
        seconds = timedelta(seconds=int(time_ms) / 1000).total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 3600) % 60
        if not shorten:
            return f"{int(hours):d}:{int(minutes):02d}:{int(seconds):02d}" if hours > 0 else f"{int(minutes):02d}:{int(seconds):02d}"
        elif hours > 0:
            return f"{int(hours):d}h\n{int(minutes)}min"
        elif minutes > 0:
            return f"{int(minutes)}min" + (f" {int(seconds)}s" if seconds > 0 else "")
        else:
            return f"{int(seconds)}s"

    @staticmethod
    def iso_to_ms(date_time: str) -> float:
        """From ISO 8601 string date to milliseconds.

        Arguments:
        date_time -- ISO 8601 date time string.

        Returns:
        date_time's milliseconds.
        """
        return isoparse(date_time).timestamp() * 1000

    @staticmethod
    def ms_to_iso(millis: int) -> str:
        """From milliseconds to ISO 8601 string date time.

        Arguments:
        millis -- date time in milliseconds.

        Returns:
        datetime string in ISO 8601 format.
        """
        return datetime.fromtimestamp(
            millis / 1000.0, tz=datetime.now(timezone.utc).astimezone().tzinfo
        ).isoformat(timespec="milliseconds")

    @staticmethod
    def dt_to_aware_locale_ms(dt: datetime):
        """From datetime to milliseconds taken time zone account.

        This function can be used to convert a UTC datetime to millis
        adding the local offset. So you'll have aware time zone datetime millis.
        """
        local_time_zone = tzlocal()
        offset_timedelta = local_time_zone.utcoffset(dt)
        return (dt.timestamp() + offset_timedelta.seconds) * 1000


class DistanceUtils:
    @staticmethod
    def m_to_str(distance_m: float) -> str:
        """From meters to human readable string.

        Arguments:
        distance_m -- distance in meters.

        Returns:
        An string representing the distance (in meters or km).
        """
        if not distance_m:
            return "-"
        elif distance_m < 1000:
            return f"{int(distance_m)} m"
        elif distance_m % 1000 == 0:
            return f"{int(distance_m / 1000)} km"
        else:
            return f"{round(distance_m / 1000, 2)} km"


class SpeedUtils:
    @staticmethod
    def mps_to_kph(speed_mps: float) -> str:
        """From meters per second to kilometeres per hour human readable.

        Arguments:
        speed_mps -- speed in meters per second.

        Returns:
        An string representing the speed_mps in a human readable format.
        """
        if not speed_mps:
            return "-"
        return str(round(speed_mps * 3.6, 1)) + " km/h"

    @staticmethod
    def mps_to_category_rate(speed_mps: float, category: str) -> str:
        if not speed_mps:
            return "-"
        if TypeActivityUtils.is_speed(category):
            return SpeedUtils.mps_to_kph(speed_mps)
        else:
            seconds = timedelta(minutes=(1000 / 60) / speed_mps).total_seconds()
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{int(minutes):d}:{int(seconds):02d} min/km"

    @staticmethod
    def mps(distance_m, time_ms):
        return distance_m / (time_ms / 1000.0)


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
            str(int(elevation_m)) + " m" if elevation_m is not None else "-"
        )

    @staticmethod
    def slope_to_str(distance: float, gain: float) -> str:
        """From distance and gain return a slope string in human way.

        Arguments:
        distance -- distance in meters.
        gain     -- gain in meters.

        Returns:
        An string representing the slope in %.
        """
        gain = gain if gain is not None else 0
        if distance:
            return str(round(gain * 100 / distance, 1)) + "%"
        else:
            return "-"


class TypeActivityUtils:
    """Utilities for activities type.

    A set of utilities for get information, icons, etc, about activity's
    type.
    """

    _types = {
        "running": {"icon": "icons/run_black_48dp.svg", "color": "#d32f2f"},
        "trail running": {"icon": "icons/run_black_48dp.svg", "color": "#c2185b"},

        "biking": {"icon": "icons/bike_black_48dp.svg", "color": "#0097a7"},
        "cycling": {"icon": "icons/bike_black_48dp.svg", "color": "#00bcd4"},
        "road biking": {"icon": "icons/bike_black_48dp.svg", "color": "#388e3c"},
        "mountain biking": {"icon": "icons/bike_black_48dp.svg", "color": "#00796b"},

        "walking": {"icon": "icons/walk_black_48dp.svg", "color": "#1976d2"},
        "trail walking": {"icon": "icons/walk_black_48dp.svg", "color": "#303f9f"},
        "hiking": {"icon": "icons/walk_black_48dp.svg", "color": "#0288d1"},
        "trail hiking": {"icon": "icons/walk_black_48dp.svg", "color": "#03a9f4"},

        "driving": {"icon": "icons/drive_car_black_48dp.svg", "color": "#5d4037"},

        "rock_climbing": {"icon": "icons/climbing_black_48dp.svg", "color": "#483e37"},

        "training": {"icon": "icons/training_black_48dp.svg", "color": "#704e89"},

        "multisport": {"icon": "icons/multisport_black_48dp.svg", "color": "#009688"},

        "transition": {"icon": "icons/transition_black_48dp.svg", "color": "#000000"},
    }

    _pace = [
        "running", "trail running", "walking", "trail walking", "hiking",
        "trail hiking"
    ]

    _color_default = "#e64a19"

    @staticmethod
    def get_icon_resource(activity_type: str) -> str:
        """Gets and returns resource path icon for activity's type."""
        if not activity_type:
            return "/es/rgmf/pyopentracks/icons/unknown_black_48dp.svg"
        activity = TypeActivityUtils._types.get(activity_type)
        if activity is None:
            return "/es/rgmf/pyopentracks/icons/unknown_black_48dp.svg"

        return "/es/rgmf/pyopentracks/" + activity["icon"]

    @staticmethod
    def get_icon_pixbuf(activity_type: str, width=48, height=48):
        """Gets GdkPixbuf.Pixbuf icon from activity type (category)."""
        res = TypeActivityUtils.get_icon_resource(activity_type)
        return GdkPixbuf.Pixbuf.new_from_resource_at_scale(
            resource_path=res,
            width=width,
            height=height,
            preserve_aspect_ratio=True
        )

    @staticmethod
    def get_activity_types():
        """Return a list with a list of two items: type's name and icon."""
        return [
            [name, data["icon"]] for name, data in TypeActivityUtils._types.items()
        ]

    @staticmethod
    def get_color(activity_type: str) -> str:
        if not activity_type:
            return TypeActivityUtils._color_default
        activity = TypeActivityUtils._types.get(activity_type)
        if activity is None:
            return TypeActivityUtils._color_default
        return activity["color"]

    @staticmethod
    def is_speed(category: str) -> bool:
        if category is None:
            return True
        return category not in TypeActivityUtils._pace


class SegmentPointUtils:

    @staticmethod
    def to_locations(segmentpoints) -> List[Location]:
        """Convert a list of track points to list of Location."""
        if not segmentpoints:
            return []
        return [sp.location for sp in segmentpoints]


class TrackPointUtils:

    @staticmethod
    def to_locations(trackpoints) -> List[Location]:
        """Convert a list of track points to list of Location."""
        if not trackpoints:
            return []
        return [tp.location for tp in trackpoints]

    @staticmethod
    def speed(tp1, tp2):
        """Returns the speed in mps between the two track points if they are not None. Otherwise returns 0."""
        if not tp1 or not tp2:
            return 0
        distance = LocationUtils.distance_between(tp1.latitude, tp1.longitude, tp2.latitude, tp2.longitude)
        time = tp2.time_ms - tp1.time_ms
        return SpeedUtils.mps(distance, time)

    @staticmethod
    def extract_dict_values(trackpoints, distance_threshold=5):
        """Returns a list with all information from trackpoints.

        It gets from trackpoints: distances, elevations, heart rates
        and locations.

        It returns the values every distance_threshold meters.

        Arguments:
        trackpoints -- track point's list (TrackPoint object's list).
        distance_threshold -- it determines points to be added (every x
                              number of meters add the track point).

        Return:
        A list with a dictionary like this:
        {
          "distance": <value in km>,
          "elevation": <value in meters>,
          "hr": <value in bpm>,
          "location": <Location object>
        }
        """
        if not trackpoints:
            return []
        result = [{
            "distance": 0,
            "elevation": float(trackpoints[0].altitude),
            "hr": float(trackpoints[0].heart_rate) if trackpoints[0].heart_rate else 0,
            "location": trackpoints[0].location
        }]
        dist_acc = 0
        total_distance = 0
        last_tp = trackpoints[0]
        for tp in trackpoints:
            dist_acc = (
                dist_acc +
                LocationUtils.distance_between(
                    last_tp.latitude, last_tp.longitude, tp.latitude, tp.longitude
                )
            )
            last_tp = tp
            if dist_acc >= distance_threshold:
                total_distance = total_distance + dist_acc
                result.append({
                    "distance": round(total_distance / 1000, 2),
                    "elevation": float(tp.altitude),
                    "hr": float(tp.heart_rate) if tp.heart_rate else 0,
                    "location": tp.location
                })
                dist_acc = 0
        return result


class LocationUtils:
    @staticmethod
    def distance_between(lat1, lon1, lat2, lon2):
        """Hervasian algorithm.

        Return:
        Distance between the two locations (lat1, lon1) to (lat2, lon2)
        in meters.
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * 6371 * asin(sqrt(a)) * 1000

    @staticmethod
    def degrees_to_semicircles(latitude, longitude):
        return latitude * (pow(2, 31) / 180), longitude * (pow(2, 31) / 180)

    @staticmethod
    def semicircles_to_degrees(latitude, longitude):
        return latitude * (180 / pow(2, 31)), longitude * (180 / pow(2, 31))


class SensorUtils:
    @staticmethod
    def hr_to_str(hr_bpm: float) -> str:
        """From float representation heart rate to heart rate.

        Arguments:
        hr_bpm -- heart rate in bpm.

        Returns:
        An string representing the heart rate.
        """
        return str(int(hr_bpm)) + " bpm" if hr_bpm is not None else "-"

    @staticmethod
    def cadence_to_str(cadence_rpm: float, category: str) -> str:
        """From float representation cadence to cadence string.

        Arguments:
        cadence_rpm -- cadence in rpm.
        category -- category of the activity.

        Returns:
        An string representing the cadence.
        """
        if not cadence_rpm:
            return "-"
        if TypeActivityUtils.is_speed(category):
            return str(int(cadence_rpm)) + " rpm"
        else:
            return str(int(float(cadence_rpm) * 2)) + " spm"

    @staticmethod
    def temperature_to_str(temperature: float) -> str:
        return str(temperature) + " ºC" if temperature is not None else "-"

    @staticmethod
    def calories_to_str(calories: int) -> str:
        return str(calories) + " calories" if calories is not None else "-"

    @staticmethod
    def weight_to_str(weight: float) -> str:
        return str(weight) + " kg" if weight is not None else "-"

    @staticmethod
    def round_to_int(value: float) -> int:
        return round(value)


class StatsUtils:
    @staticmethod
    def avg_per_month(num: int, year: int) -> float:
        current_year, current_month, _ = DateUtils.get_today()
        if current_year == year:
            return round(num / current_month, 2)
        return round(num / 12, 2)


class ZonesUtils:
    _colors = {
        "z1": "#a6a6a6",
        "z2": "#3b97f3",
        "z3": "#82c91e",
        "z4": "#f98925",
        "z5": "#d32020",
    }

    @staticmethod
    def description_hr_zone(zone_code: str) -> str:
        if zone_code.lower() == "z1":
            return "Warm Up"
        elif zone_code.lower() == "z2":
            return "Endurance"
        elif zone_code.lower() == "z3":
            return "Tempo"
        elif zone_code.lower() == "z4":
            return "Threshold"
        elif zone_code.lower() == "z5":
            return "VO2Max"
        else:
            return "Unknown"


    @staticmethod
    def get_color(zone_code: str) -> str:
        if zone_code.lower() == "z5":
            return ZonesUtils._colors["z5"]
        elif zone_code.lower() == "z4":
            return ZonesUtils._colors["z4"]
        elif zone_code.lower() == "z3":
            return ZonesUtils._colors["z3"]
        elif zone_code.lower() == "z2":
            return ZonesUtils._colors["z2"]
        else:
            return ZonesUtils._colors["z1"]


class SanitizeFile:
    @staticmethod
    def fit_file(path: str) -> str:
        """Get an expected fit file path and return a sanitized fit file."""
        if not path:
            return "noname.fit"

        root, ext = os.path.splitext(path)
        if not ext or ext != ".fit":
            return root + ".fit"
        else:
            return path
