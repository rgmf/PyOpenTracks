from mock_db import MockDB

from pyopentracks.tasks.gain_loss_filter import GainLossFilter
from pyopentracks.utils.utils import LocationUtils


class TestGainLossFilter(MockDB):
    def test_gain_loss_filter_1(self):
        """Flat terrain, all track points with gain and loss set to 0."""
        trackid = self.add_track_with_trackpoints(num_tp=4)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(self.get_trackpoints(trackid)) == 4)

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 0)
        self.assertEquals(track.loss_elevation_m, 0)

    def test_gain_loss_filter_2(self):
        """Flat terrain with 10 track points."""
        num_points = 10
        distance_between_tp = 10

        trackid = self.add_track_with_trackpoints(
            num_tp=num_points,
            distance_between_tp=distance_between_tp
        )
        trackpoints = self.get_trackpoints(trackid)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(trackpoints) == num_points)

        distance = 0
        last_tp = trackpoints[0]
        for tp in self.get_trackpoints(trackid):
            distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude,
                tp.latitude, tp.longitude
            )
            last_tp = tp
        self.assertAlmostEquals(
            distance,
            (num_points - 1) * distance_between_tp,
            0
        )

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 0)
        self.assertEquals(track.loss_elevation_m, 0)

    def test_gain_loss_filter_3(self):
        """Set of track points with one of them set with 3m gain."""
        num_points = 10
        distance_between_tp = 10

        trackid = self.add_track_with_trackpoints(
            num_tp=num_points,
            distance_between_tp=distance_between_tp
        )
        trackpoints = self.get_trackpoints(trackid)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(trackpoints) == num_points)

        distance = 0
        last_tp = trackpoints[0]
        last_tp.set_elevation_gain(3)
        self.update(last_tp)
        for tp in trackpoints:
            distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude,
                tp.latitude, tp.longitude
            )
            last_tp = tp
        self.assertAlmostEquals(
            distance,
            (num_points - 1) * distance_between_tp,
            0
        )

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 3)
        self.assertEquals(track.loss_elevation_m, 0)

    def test_gain_loss_filter_4(self):
        """Climbing/Descending bad. All points with 3m gain and 3m loss."""
        num_points = 10
        distance_between_tp = 10

        trackid = self.add_track_with_trackpoints(
            num_tp=num_points,
            distance_between_tp=distance_between_tp
        )
        trackpoints = self.get_trackpoints(trackid)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(trackpoints) == num_points)

        distance = 0
        last_tp = trackpoints[0]
        for tp in trackpoints:
            tp.set_elevation_gain(3)
            tp.set_elevation_loss(3)
            self.update(tp)
            distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude,
                tp.latitude, tp.longitude
            )
            last_tp = tp
        self.assertAlmostEquals(
            distance,
            (num_points - 1) * distance_between_tp,
            0
        )

        trackpoints_after = self.get_trackpoints(trackid)

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 0)
        self.assertEquals(track.loss_elevation_m, 0)
        self.assertEquals(
            sum([tp.elevation_gain for tp in trackpoints_after]),
            num_points * 3
        )
        self.assertEquals(
            sum([tp.elevation_loss for tp in trackpoints_after]),
            num_points * 3
        )

    def test_gain_loss_filter_5(self):
        """With errors. All points with 3m gain and one with 3m loss."""
        num_points = 10
        distance_between_tp = 10

        trackid = self.add_track_with_trackpoints(
            num_tp=num_points,
            distance_between_tp=distance_between_tp
        )
        trackpoints = self.get_trackpoints(trackid)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(trackpoints) == num_points)

        distance = 0
        last_tp = trackpoints[0]
        for idx, tp in enumerate(trackpoints):
            tp.set_elevation_gain(3)
            tp.set_elevation_loss(3 if idx == 0 else 0)
            self.update(tp)
            distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude,
                tp.latitude, tp.longitude
            )
            last_tp = tp
        self.assertAlmostEquals(
            distance,
            (num_points - 1) * distance_between_tp,
            0
        )

        trackpoints_after = self.get_trackpoints(trackid)

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 12)
        self.assertEquals(track.loss_elevation_m, 0)
        self.assertEquals(
            sum([tp.elevation_gain for tp in trackpoints_after]),
            num_points * 3
        )
        self.assertEquals(
            sum([tp.elevation_loss for tp in trackpoints_after]),
            3
        )

    def test_gain_loss_filter_6(self):
        """With errors. All points with 3m loss and one with 3m gain."""
        num_points = 10
        distance_between_tp = 10

        trackid = self.add_track_with_trackpoints(
            num_tp=num_points,
            distance_between_tp=distance_between_tp
        )
        trackpoints = self.get_trackpoints(trackid)

        self.assertTrue(trackid is not None)
        self.assertTrue(len(trackpoints) == num_points)

        distance = 0
        last_tp = trackpoints[0]
        for idx, tp in enumerate(trackpoints):
            tp.set_elevation_gain(3 if idx == 0 else 0)
            tp.set_elevation_loss(3)
            self.update(tp)
            distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude,
                tp.latitude, tp.longitude
            )
            last_tp = tp
        self.assertAlmostEquals(
            distance,
            (num_points - 1) * distance_between_tp,
            0
        )

        trackpoints_after = self.get_trackpoints(trackid)

        with self.mock_db_config:
            GainLossFilter(trackid).run()

        track = self.get_track(trackid)
        self.assertEquals(track.gain_elevation_m, 0)
        self.assertEquals(track.loss_elevation_m, 12)
        self.assertEquals(
            sum([tp.elevation_gain for tp in trackpoints_after]),
            3
        )
        self.assertEquals(
            sum([tp.elevation_loss for tp in trackpoints_after]),
            num_points * 3
        )
