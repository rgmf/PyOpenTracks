from datetime import datetime

from mock_db import MockDB

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.activity import Track


class TestAggregatedStats(MockDB):

    def _create_track(
        self,
        category,
        time_ms,
        movingtime_ms,
        distance_m,
        avgspeed_mps,
        avgmovingspeed_mps,
        maxspeed_mps,
        gain_m=None,
        loss_m=None,
        maxhr=None,
        avghr=None,
        maxcadence=None,
        avgcadence=None,
        starttime_str=None,
        endtime_str=None,
        recorded_with="PyOpenTracksTests"
    ):
        eight_hours_ms = 8 * 60 * 60 * 1000
        time_now_ms = datetime.timestamp(datetime.now()) * 1000
        starttime_ms = time_now_ms - eight_hours_ms if not starttime_str \
          else datetime.timestamp(datetime.fromisoformat(starttime_str)) * 1000
        stoptime_ms = starttime_ms + time_ms if not endtime_str \
          else datetime.timestamp(datetime.fromisoformat(endtime_str)) * 1000

        return Track(
            None, None, f"Track {time_now_ms}", "Track Description", category,
            starttime_ms, stoptime_ms, distance_m, time_ms, movingtime_ms,
            avgspeed_mps, avgmovingspeed_mps, maxspeed_mps,
            0, 0, gain_m, loss_m, maxhr, avghr, maxcadence, avgcadence, recorded_with
        )

    def test_aggregated_stats_empty(self):
        """Aggregated stats from empty track table."""
        with self.mock_db_config:
            aggregated_stats = DatabaseHelper.get_aggregated_stats()
            self.assertIsNone(aggregated_stats)

    def test_aggregated_stats_1(self):
        """Aggregated stats only for one category.

        With neither sensor data nor elevation gain and loss.
        """
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        diff = 3

        with self.mock_db_config:
            for value in values:
                DatabaseHelper.insert(
                    self._create_track(
                        category="biking",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=(value + diff) * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value + diff,
                        maxspeed_mps=value + diff + diff
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._category, "biking")
            self.assertEqual(a._total_activities, len(values))
            self.assertEqual(
                a._total_time_ms,
                sum(map(lambda v: v + diff, values)) * 60 * 1000
            )
            self.assertEqual(a._total_moving_time_ms, sum(values) * 60 * 1000)
            self.assertEqual(a._total_distance_m, sum(values))
            self.assertIsNone(a._total_elevation_gain_m)
            self.assertEqual(
                a._avg_time_ms,
                sum(map(lambda v: v + diff, values)) * 60 * 1000 / len(values)
            )
            self.assertEqual(
                a._avg_moving_time_ms,
                sum(values) * 60 * 1000 / len(values)
            )
            self.assertEqual(a._avg_distance_m, sum(values) / len(values))
            self.assertIsNone(a._avg_elevation_gain_m)
            self.assertEqual(
                a._avg_speed_mps,
                sum(values) / (sum(values) * 60)
            )
            self.assertIsNone(a._avg_heart_rate_bpm)
            self.assertEqual(a._max_time_ms, 63 * 60 * 1000)
            self.assertEqual(a._max_moving_time_ms, 60 * 60 * 1000)
            self.assertEqual(a._max_distance_m, 60)
            self.assertIsNone(a._max_elevation_gain_m)
            self.assertEqual(a._max_speed_mps, 66)
            self.assertIsNone(a._max_heart_rate_bpm)

    def test_aggregated_stats_2(self):
        """Aggregated stats for three categories.

        With neither sensor data nor elevation gain and loss.
        """
        categories = ["biking", "cycling", "trekking"]
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        diff = 3

        with self.mock_db_config:
            for category in categories:
                for value in values:
                    DatabaseHelper.insert(
                        self._create_track(
                            category=category,
                            starttime_str="2021-01-01T08:30:30",
                            endtime_str="2021-01-01T10:30:30",
                            time_ms=(value + diff) * 60 * 1000,
                            movingtime_ms=value * 60 * 1000,
                            distance_m=value,
                            avgspeed_mps=value,
                            avgmovingspeed_mps=value + diff,
                            maxspeed_mps=value + diff + diff
                        )
                    )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 3)

            categories_copy = categories.copy()
            for i, v in enumerate(categories):
                a = aggregated_list[i]
                self.assertTrue(a._category in categories_copy)
                categories_copy.remove(a._category)
                self.assertEqual(a._total_activities, len(values))
                self.assertEqual(
                    a._total_time_ms,
                    sum(map(lambda v: v + diff, values)) * 60 * 1000
                )
                self.assertEqual(a._total_moving_time_ms, sum(values) * 60 * 1000)
                self.assertEqual(a._total_distance_m, sum(values))
                self.assertIsNone(a._total_elevation_gain_m)
                self.assertEqual(
                    a._avg_time_ms,
                    sum(map(lambda v: v + diff, values)) * 60 * 1000 / len(values)
                )
                self.assertEqual(
                    a._avg_moving_time_ms,
                    sum(values) * 60 * 1000 / len(values)
                )
                self.assertEqual(a._avg_distance_m, sum(values) / len(values))
                self.assertIsNone(a._avg_elevation_gain_m)
                self.assertEqual(
                    a._avg_speed_mps,
                    sum(values) / (sum(values) * 60)
                )
                self.assertIsNone(a._avg_heart_rate_bpm)
                self.assertEqual(a._max_time_ms, 63 * 60 * 1000)
                self.assertEqual(a._max_moving_time_ms, 60 * 60 * 1000)
                self.assertEqual(a._max_distance_m, 60)
                self.assertIsNone(a._max_elevation_gain_m)
                self.assertEqual(a._max_speed_mps, 66)
                self.assertIsNone(a._max_heart_rate_bpm)

            self.assertEqual(len(categories_copy), 0)

    def test_aggregated_stats_3(self):
        """Order in aggregated stats for two categories.

        With neither sensor data nor elevation gain and loss.

        Check the order of aggregated stats: more total activities goes first.
        """
        values_running = [5, 10]
        values_cycling = [10, 20, 30]

        with self.mock_db_config:
            for value in values_cycling:
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value
                    )
                )

            for value in values_running:
                DatabaseHelper.insert(
                    self._create_track(
                        category="running",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value
                    )
                )

            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 2)
            self.assertEqual(aggregated_list[0].category, "cycling")
            self.assertEqual(aggregated_list[1].category, "running")

    def test_aggregated_stats_4(self):
        """Aggregated stats with elevation gain and loss."""
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with self.mock_db_config:
            for i, value in enumerate(values):
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value,
                        gain_m=value,
                        loss_m=value
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._avg_elevation_gain_m, sum(values) / len(values))
            self.assertEqual(a._max_elevation_gain_m, 60)

    def test_aggregated_stats_5(self):
        """Aggregated stats with elevation gain and loss."""
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with self.mock_db_config:
            for i, value in enumerate(values):
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value,
                        gain_m=value if i % 2 == 0 else None,
                        loss_m=value if i % 2 == 0 else None
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._avg_elevation_gain_m, 180 / 6)
            self.assertEqual(a._max_elevation_gain_m, 55)

    def test_aggregated_stats_6(self):
        """Aggregated stats with hr sensor data."""
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with self.mock_db_config:
            for i, value in enumerate(values):
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value,
                        maxhr=value,
                        avghr=value
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._max_heart_rate_bpm, 60)
            self.assertEqual(a._avg_heart_rate_bpm, sum(values) / len(values))

    def test_aggregated_stats_7(self):
        """Aggregated stats with elevation gain and loss.

        Without sensor data.
        """
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with self.mock_db_config:
            for i, value in enumerate(values):
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value,
                        maxhr=value if i % 2 == 0 else None,
                        avghr=value if i % 2 == 0 else None
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._max_heart_rate_bpm, 55)
            self.assertEqual(a._avg_heart_rate_bpm,  180 / 6)

    def test_aggregated_stats_8(self):
        """Aggregated stats with only one activity with values for sensors."""
        values = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with self.mock_db_config:
            for i, value in enumerate(values):
                DatabaseHelper.insert(
                    self._create_track(
                        category="cycling",
                        starttime_str="2021-01-01T08:30:30",
                        endtime_str="2021-01-01T10:30:30",
                        time_ms=value * 60 * 1000,
                        movingtime_ms=value * 60 * 1000,
                        distance_m=value,
                        avgspeed_mps=value,
                        avgmovingspeed_mps=value,
                        maxspeed_mps=value,
                        gain_m=value if i == 0 else None,
                        loss_m=value if i == 0 else None,
                        maxhr=value if i == 0 else None,
                        avghr=value if i == 0 else None
                    )
                )
            aggregated_list = DatabaseHelper.get_aggregated_stats()
            self.assertIsNotNone(aggregated_list)
            self.assertEqual(len(aggregated_list), 1)

            a = aggregated_list[0]
            self.assertEqual(a._max_heart_rate_bpm, 5)
            self.assertEqual(a._avg_heart_rate_bpm, 5)
            self.assertEqual(a._max_heart_rate_bpm, 5)
            self.assertEqual(a._avg_heart_rate_bpm, 5)
