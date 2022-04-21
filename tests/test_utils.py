import unittest
# import sys

# pkgdatadir = "/home/roman/workspace/PyOpenTracks/buildir/buildir/testdir/share/pyopentracks/data"
# sys.path.insert(1, pkgdatadir)

from datetime import datetime, timezone


from pyopentracks.models.track_point import TrackPoint
from pyopentracks.models.location import Location
from pyopentracks.utils.utils import (
    StatsUtils,
    TimeUtils,
    DateTimeUtils,
    DateUtils,
    DistanceUtils,
    SpeedUtils,
    ElevationUtils,
    TypeActivityUtils,
    TrackPointUtils,
    LocationUtils,
    SensorUtils
)


class TestDateTimeUtils(unittest.TestCase):
    def test_begin_of_day(self):
        dt = datetime.fromtimestamp(
            DateTimeUtils.begin_of_day(2022, 1, 1) / 1000.0
        )
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)

    def test_end_of_day(self):
        dt = datetime.fromtimestamp(
            DateTimeUtils.end_of_day(2022, 1, 1) / 1000.0
        )
        self.assertEqual(dt.hour, 23)
        self.assertEqual(dt.minute, 59)
        self.assertEqual(dt.second, 59)

    def test_ms_to_str(self):
        naive_dt = datetime(2022, 1, 1, 10, 30, 15)
        self.assertEqual(
            DateTimeUtils.ms_to_str(naive_dt.timestamp() * 1000.0),
            "Sat, 01 Jan 2022 10:30:15"
        )
        self.assertEqual(
            DateTimeUtils.ms_to_str(naive_dt.timestamp() * 1000.0, True),
            "01 Jan 2022"
        )

    def test_first_day_ms(self):
        jan_2022 = 1640991600000
        self.assertEqual(DateTimeUtils.first_day_ms(2022, 1), jan_2022)

    def test_last_day_ms(self):
        jan_2022 = 1643669999000
        self.assertEqual(DateTimeUtils.last_day_ms(2022, 1), jan_2022)
        feb_2021 = 1614553199000
        self.assertEqual(DateTimeUtils.last_day_ms(2021, 2), feb_2021)
        feb_2004 = 1078095599000
        self.assertEqual(DateTimeUtils.last_day_ms(2004, 2), feb_2004)


class TestDateUtils(unittest.TestCase):
    def test_get_months(self):
        months = DateUtils.get_months()
        self.assertEqual(len(months), 12)
        self.assertTrue(isinstance(months, list))

    def test_get_month_name(self):
        self.assertEqual(DateUtils.get_month_name(1), "enero")
        self.assertEqual(DateUtils.get_month_name(2), "febrero")
        self.assertEqual(DateUtils.get_month_name(3), "marzo")
        self.assertEqual(DateUtils.get_month_name(4), "abril")
        self.assertEqual(DateUtils.get_month_name(5), "mayo")
        self.assertEqual(DateUtils.get_month_name(6), "junio")
        self.assertEqual(DateUtils.get_month_name(7), "julio")
        self.assertEqual(DateUtils.get_month_name(8), "agosto")
        self.assertEqual(DateUtils.get_month_name(9), "septiembre")
        self.assertEqual(DateUtils.get_month_name(10), "octubre")
        self.assertEqual(DateUtils.get_month_name(11), "noviembre")
        self.assertEqual(DateUtils.get_month_name(12), "diciembre")
        self.assertEqual(DateUtils.get_month_name(15), "enero")
        self.assertEqual(DateUtils.get_month_name(0), "enero")

    def test_get_today(self):
        year, month, day = DateUtils.get_today()
        self.assertTrue(isinstance(year, int))
        self.assertTrue(isinstance(month, int) and 0 <= month < 12)
        self.assertTrue(isinstance(day, int))


class TestTimeUtils(unittest.TestCase):
    def test_valid_iso_to_ms(self):
        valid_iso_8601 = [
            "2022-01-01",
            "2022-01-01T08:30:50",
            "2022-01-01T08:30:50.5",
            "2022-01-01T08:30:50.50",
            "2022-01-01T08:30:50.500",
            "2022-01-01T08:30:50.5000",
            "2022-01-01T08:30:50.50000",
            "2022-01-01T08:30:50.500000",
            "2022-01-01T08:30:50Z",
            "2022-01-01T08:30:50.5Z",
            "2022-01-01T08:30:50.50Z",
            "2022-01-01T08:30:50.500Z",
            "2022-01-01T08:30:50.5000Z",
            "2022-01-01T08:30:50.50000Z",
            "2022-01-01T08:30:50.500000Z",
            "2022-01-01T08:30:50+01:00",
            "2022-01-01T08:30:50.5+01:00",
            "2022-01-01T08:30:50.50+01:00",
            "2022-01-01T08:30:50.500+01:00",
            "2022-01-01T08:30:50.5000+01:00",
            "2022-01-01T08:30:50.50000+01:00",
            "2022-01-01T08:30:50.500000+01:00",
            "2022-01-01T08:30:50.500000-01:00",
            "2022-01-01T08:30:50.500000+01:30",
            "2022-01-01T08:30:50.500000-01:30",
        ]
        for i in valid_iso_8601:
            self.assertTrue(TimeUtils.iso_to_ms(i) > 0)

    def test_invalid_iso_to_ms(self):
        invalid_iso_8601 = [
            "2022-1-1",
            "2022-01-0108:30:50",
            "2022-01-01T8:3:5",
            "01-01-2022T08:30:50",
            "22-01-01T08:30:50",
            "2022-01-01T08:30:50+24:00",
            "2022-01-01T08:30:50-24:00",
            "2022010108:30:50",
        ]
        for i in invalid_iso_8601:
            with self.assertRaises(Exception):
                TimeUtils.iso_to_ms(i)

    def test_ms_to_iso(self):
        ms = 1641029415000
        timezone_obj = datetime.now(timezone.utc).astimezone().tzinfo
        timedelta_obj = timezone_obj.utcoffset(None)
        hours = timedelta_obj.seconds / 60 / 60
        minutes = (timedelta_obj.seconds / 60) % 60
        offset_str = f"{int(hours):+03}:{int(minutes):02}"
        self.assertEqual(
            TimeUtils.ms_to_iso(ms),
            f"2022-01-01T10:30:15.000{offset_str}"
        )

    def test_utc_offset_str(self):
        timezone_obj = datetime.now(timezone.utc).astimezone().tzinfo
        timedelta_obj = timezone_obj.utcoffset(None)
        hours = timedelta_obj.seconds / 60 / 60
        minutes = (timedelta_obj.seconds / 60) % 60
        offset_str = f"{int(hours):+03}:{int(minutes):02}"
        self.assertEqual(TimeUtils.utc_offset_str(), offset_str)

    def test_ms_to_str(self):
        time_ms = ((10 * 3600) + (30 * 60) + 15) * 1000
        self.assertEqual(TimeUtils.ms_to_str(time_ms, True), "10h\n30min")
        self.assertEqual(TimeUtils.ms_to_str(time_ms, False), "10:30:15")

    def test_dt_to_aware_locale_ms(self):
        # Winter time
        dt_utc = datetime(2020, 1, 1, 7, 0, 0)
        ms = TimeUtils.dt_to_aware_locale_ms(dt_utc)
        dt_local = datetime.fromtimestamp(ms / 1000)
        self.assertEqual(dt_utc.hour + 1, dt_local.hour)

        # Summer time
        dt_utc = datetime(2020, 8, 1, 7, 0, 0)
        ms = TimeUtils.dt_to_aware_locale_ms(dt_utc)
        dt_local = datetime.fromtimestamp(ms / 1000)
        self.assertEqual(dt_utc.hour + 2, dt_local.hour)


class TestDistanceUtils(unittest.TestCase):
    def test_m_to_str(self):
        self.assertEqual(DistanceUtils.m_to_str(None), "-")
        self.assertEqual(DistanceUtils.m_to_str(999), "999 m")
        self.assertEqual(DistanceUtils.m_to_str(999.99), "999 m")
        self.assertEqual(DistanceUtils.m_to_str(1000), "1 km")
        self.assertEqual(DistanceUtils.m_to_str(84000), "84 km")
        self.assertEqual(DistanceUtils.m_to_str(84525), "84.53 km")
        self.assertEqual(DistanceUtils.m_to_str(84500.683), "84.5 km")


class TestSpeedUtils(unittest.TestCase):
    def test_mps_to_kph(self):
        self.assertEqual(SpeedUtils.mps_to_kph(None), "-")
        self.assertEqual(SpeedUtils.mps_to_kph(1), "3.6 km/h")
        self.assertEqual(SpeedUtils.mps_to_kph(5.55555556), "20.0 km/h")
        self.assertEqual(SpeedUtils.mps_to_kph(7.1527778), "25.8 km/h")

    def test_mps_to_category_rate(self):
        self.assertEqual(
            SpeedUtils.mps_to_category_rate(7.1527778, "cycling"),
            "25.8 km/h"
        )
        self.assertEqual(
            SpeedUtils.mps_to_category_rate(5.55555556, "running"),
            "3:00 min/km"
        )
        self.assertEqual(
            SpeedUtils.mps_to_category_rate(3.75, "running"),
            "4:26 min/km"
        )

    def test_mps(self):
        self.assertEqual(SpeedUtils.mps(1, 1000), 1.0)
        self.assertEqual(SpeedUtils.mps(1, 100), 10.0)


class TestElevationUtils(unittest.TestCase):
    def test_elevation_to_str(self):
        self.assertEqual(ElevationUtils.elevation_to_str(None), "-")
        self.assertEqual(ElevationUtils.elevation_to_str(15.5), "15 m")
        self.assertEqual(ElevationUtils.elevation_to_str(0), "0 m")

    def test_slope_to_str(self):
        self.assertEqual(ElevationUtils.slope_to_str(None, None), "-")
        self.assertEqual(ElevationUtils.slope_to_str(100, None), "0.0%")
        self.assertEqual(ElevationUtils.slope_to_str(None, 100), "-")
        self.assertEqual(ElevationUtils.slope_to_str(0, 0), "-")
        self.assertEqual(ElevationUtils.slope_to_str(100, 0), "0.0%")
        self.assertEqual(ElevationUtils.slope_to_str(0, 100), "-")
        self.assertEqual(ElevationUtils.slope_to_str(100, 1), "1.0%")
        self.assertEqual(ElevationUtils.slope_to_str(4000, 200), "5.0%")


class TestTypeActivityUtils(unittest.TestCase):
    def test_get_icon_resource(self):
        self.assertEqual(
            TypeActivityUtils.get_icon_resource(None),
            "/es/rgmf/pyopentracks/icons/unknown_black_48dp.svg"
        )
        self.assertEqual(
            TypeActivityUtils.get_icon_resource("not exists"),
            "/es/rgmf/pyopentracks/icons/unknown_black_48dp.svg"
        )
        for category in ["running", "trail running"]:
            self.assertEqual(
                TypeActivityUtils.get_icon_resource(category),
                "/es/rgmf/pyopentracks/icons/run_black_48dp.svg"
            )
        for category in [
            "biking", "cycling", "road biking", "mountain biking"
        ]:
            self.assertEqual(
                TypeActivityUtils.get_icon_resource(category),
                "/es/rgmf/pyopentracks/icons/bike_black_48dp.svg"
            )
        for category in [
            "walking", "trail walking", "hiking", "trail hiking"
        ]:
            self.assertEqual(
                TypeActivityUtils.get_icon_resource(category),
                "/es/rgmf/pyopentracks/icons/walk_black_48dp.svg"
            )
        self.assertEqual(
            TypeActivityUtils.get_icon_resource("driving"),
            "/es/rgmf/pyopentracks/icons/drive_car_black_48dp.svg"
        )

    def test_is_speed(self):
        for category in [
            "running", "trail running", "walking", "trail walking", "hiking",
            "trail hiking"
        ]:
            self.assertFalse(TypeActivityUtils.is_speed(category))
        for category in [
            None, "not exists",
            "biking", "cycling", "road biking", "mountain biking", "driving"
        ]:
            self.assertTrue(TypeActivityUtils.is_speed(category))


class TestTrackPointUtils(unittest.TestCase):
    def test_to_locations(self):
        tp1 = TrackPoint(0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        tp2 = TrackPoint(0, 0, 0, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        tp3 = TrackPoint(0, 0, 0, 6, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        tp4 = TrackPoint(0, 0, 0, 8, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(
            [(loc.latitude, loc.longitude) for loc in TrackPointUtils.to_locations([tp1, tp2, tp3, tp4])],
            [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (7.0, 8.0)]
        )

    def test_speed(self):
        tp1 = TrackPoint(0, 0, 0, -73.96592, 40.78395, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        tp2 = TrackPoint(0, 0, 0, -73.96537, 40.78378, 10000, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertAlmostEqual(TrackPointUtils.speed(tp1, tp2), 5, 2)

    def test_extract_dict_values(self):
        tp1 = TrackPoint(0, 0, 0, -73.96592, 40.78395, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        tp2 = TrackPoint(0, 0, 0, -73.96537, 40.78378, 10000, 0, 0, 0, 0, 0, 0, 0, 0)
        tp3 = TrackPoint(0, 0, 0, -73.96537, 40.78378, 20000, 0, 0, 0, 0, 0, 0, 0, 0)
        tp4 = TrackPoint(0, 0, 0, -73.96592, 40.78395, 30000, 0, 0, 0, 0, 0, 0, 0, 0)
        tp5 = TrackPoint(0, 0, 0, -73.96592, 40.78395, 40000, 0, 0, 0, 0, 0, 0, 0, 0)
        tp6 = TrackPoint(0, 0, 0, -73.96537, 40.78378, 50000, 0, 0, 0, 0, 0, 0, 0, 0)
        tpoints = [tp1, tp2, tp3, tp4, tp5, tp6]
        dict_list = TrackPointUtils.extract_dict_values(tpoints, 50)
        self.assertEqual(len(dict_list), 4)
        for dictionary in dict_list:
            self.assertTrue(isinstance(dictionary, dict))
            self.assertTrue("distance" in dictionary)
            self.assertTrue(isinstance(dictionary["distance"], (int, float)))
            self.assertTrue("elevation" in dictionary)
            self.assertTrue(isinstance(dictionary["elevation"], (int, float)))
            self.assertTrue("hr" in dictionary)
            self.assertTrue(isinstance(dictionary["hr"], (int, float)))
            self.assertTrue("location" in dictionary)
            self.assertTrue(isinstance(dictionary["location"], Location))
            self.assertTrue(isinstance(dictionary["location"].latitude, float))
            self.assertTrue(isinstance(dictionary["location"].longitude, float))


class TestLocationUtils(unittest.TestCase):
    def test_distance_between(self):
        self.assertAlmostEqual(
            LocationUtils.distance_between(
                40.78395, -73.96592, 40.78378, -73.96537
            ),
            50,
            1
        )


class TestSensorUtils(unittest.TestCase):
    def test_hr_to_str(self):
        self.assertEqual(SensorUtils.hr_to_str(None), "-")
        self.assertEqual(SensorUtils.hr_to_str(0), "0 bpm")
        self.assertEqual(SensorUtils.hr_to_str(95.87), "95 bpm")

    def test_cadence_to_str(self):
        self.assertEqual(SensorUtils.cadence_to_str(None), "-")
        self.assertEqual(SensorUtils.cadence_to_str(0), "0 rpm")
        self.assertEqual(SensorUtils.cadence_to_str(95.87), "95 rpm")


class TestStatsUtils(unittest.TestCase):
    def test_avg_per_month(self):
        self.assertEqual(StatsUtils.avg_per_month(12, 2008), 1.0)


if __name__ == "__main__":
    unittest.main()
