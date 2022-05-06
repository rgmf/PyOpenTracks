import sys

pkgdatadir = "/home/roman/workspace/PyOpenTracks/buildir/buildir/testdir/share/pyopentracks/data"
sys.path.insert(1, pkgdatadir)

import unittest

from pyopentracks.stats.track_stats import HrZonesStats


class TrackPoint:
    def __init__(self, ms, hr, segment):
        self.time_ms = ms
        self.heart_rate = hr
        self.segment = segment


class TestHrZonesStats(unittest.TestCase):
    def test_get_zone_idx(self):
        zones = [10, 20, 30, 40, 50]
        obj = HrZonesStats(zones)
        self.assertEqual(obj._get_zone_idx(9), -1)
        self.assertEqual(obj._get_zone_idx(10), 0)
        self.assertEqual(obj._get_zone_idx(11), 0)
        self.assertEqual(obj._get_zone_idx(19), 0)
        self.assertEqual(obj._get_zone_idx(20), 1)
        self.assertEqual(obj._get_zone_idx(21), 1)
        self.assertEqual(obj._get_zone_idx(29), 1)
        self.assertEqual(obj._get_zone_idx(30), 2)
        self.assertEqual(obj._get_zone_idx(31), 2)
        self.assertEqual(obj._get_zone_idx(39), 2)
        self.assertEqual(obj._get_zone_idx(40), 3)
        self.assertEqual(obj._get_zone_idx(41), 3)
        self.assertEqual(obj._get_zone_idx(49), 3)
        self.assertEqual(obj._get_zone_idx(50), 4)
        self.assertEqual(obj._get_zone_idx(51), 4)
        self.assertEqual(obj._get_zone_idx(59), 4)

    def test_compute(self):
        zones = [10, 20, 30, 40, 50]
        tp = [
            TrackPoint(0, 5, 1),
            TrackPoint(1, 3, 1),
            TrackPoint(2, 7, 1),

            TrackPoint(3, 12, 1),
            TrackPoint(4, 13, 1),
            TrackPoint(5, 11, 1),
            TrackPoint(6, 14, 1),
            TrackPoint(7, 19, 1),

            TrackPoint(8, 20, 1),
            TrackPoint(9, 21, 1),
            TrackPoint(10, 20, 1),

            TrackPoint(11, 19, 1),

            TrackPoint(12, 22, 1),

            TrackPoint(13, 40, 1),
            TrackPoint(14, 50, 1),
            TrackPoint(15, 60, 1),
            TrackPoint(16, 55, 1),
        ]
        obj = HrZonesStats(zones)
        stats = obj.compute(tp)
        self.assertEqual(stats[0], 6)
        self.assertEqual(stats[1], 4)
        self.assertEqual(stats[2], 0)
        self.assertEqual(stats[3], 1)
        self.assertEqual(stats[4], 2)

    def test_compute_with_no_hr(self):
        class TrackPoint:
            def __init__(self, ms, hr, segment):
                self.time_ms = ms
                self.heart_rate = hr
                self.segment = segment
        zones = [10, 20, 30, 40, 50]
        tp = [
            TrackPoint(0, None, 1),
            TrackPoint(1, None, 1),
            TrackPoint(2, 11, 1),
            TrackPoint(3, 14, 1),
            TrackPoint(4, None, 1),

            TrackPoint(5, 20, 1),
            TrackPoint(6, None, 1),
            TrackPoint(7, 20, 1),

            TrackPoint(8, 19, 1),

            TrackPoint(9, 22, 1),
        ]
        obj = HrZonesStats(zones)
        stats = obj.compute(tp)
        self.assertEqual(stats[0], 3)
        self.assertEqual(stats[1], 2)
        self.assertEqual(stats[2], 0)
        self.assertEqual(stats[3], 0)
        self.assertEqual(stats[4], 0)
