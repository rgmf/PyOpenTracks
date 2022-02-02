import os

from mock_db import MockDB

from pyopentracks.io.gpx_parser import GpxParserHandler
from pyopentracks.io.result import Result
from pyopentracks.io.export_handler import ExportTrack
from pyopentracks.models.database_helper import DatabaseHelper


class TestImportExport(MockDB):

    def _import_export_import(self, filename, import_func):
        """Import, export and import again filename using import_func."""
        # Import the original file.
        track = import_func(filename)

        # Export to another file.
        folder = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets"
        )
        exported_filename = os.path.join(
            folder,
            str(track.id) + track.name + ".gpx"
        )
        with self.mock_db_config:
            ExportTrack(track.id, folder).run()
        self.assertTrue(os.path.isfile(exported_filename))

        # Delete track from database to import once again from just exported
        # file. The result of import -> export -> import should be the same.
        with self.mock_db_config:
            DatabaseHelper.delete(track)
        import_func(exported_filename)

        # Remove exported file.
        os.remove(exported_filename)

    def test_import_gpx_1(self):
        """Test import a simple GPX with 6 track points.

        It's a simple GPX file with 6 track points, without speed tag, recorded
        with OpenTracks, with elevation gain of 1 for each track point and a
        heart rate of 100 for each track point.
        """
        def import_file(filename):
            with self.mock_db_config:
                parser = GpxParserHandler()
                result = parser.parse(filename)
                self.assertTrue(result.code is Result.OK)
                self.assertTrue(result.track is not None)
                self.assertTrue(result.track.track_points is not None)
                self.assertEqual(len(result.track.track_points), 6)

                trackid = DatabaseHelper.insert(result.track)
                self.assertTrue(trackid is not None)

                DatabaseHelper.bulk_insert(result.track.track_points, trackid)

                tracks = DatabaseHelper.get_tracks()
                self.assertEqual(len(tracks), 1)

                track = tracks[0]
                self.assertEqual(track.name, "For tests")
                self.assertEqual(
                    track.description,
                    "This is a GPX created for tests"
                )
                self.assertEqual(track.activity_type, "road biking")
                self.assertEqual(track._totaltime_ms, 20_000)
                self.assertEqual(track._movingtime_ms, 20_000)
                self.assertEqual(track.gain_elevation_m, 6)
                self.assertIsNone(track.loss_elevation_m)
                self.assertEqual(track._maxhr_bpm, 100)
                self.assertEqual(track._avghr_bpm, 100)
                self.assertEqual(track._avgspeed_mps, track._totaldistance_m / 20)
                self.assertEqual(
                    track._avgmovingspeed_mps,
                    track._totaldistance_m / 20
                )

                track_points = DatabaseHelper.get_track_points(track.id)
                self.assertEqual(len(track_points), 6)
                self.assertEqual(track_points[-1].segment, 1)

                return track

        # Import -> Export -> Import.
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_one_segment_no_speed_tag.gpx"
        )
        self._import_export_import(filename, import_file)

    def test_import_gpx_2(self):
        """Test import a simple GPX with 11 track points and 2 segments.

        This gpx file contains 11 points in a trkseg but from track point 6 to
        7 speed is zero so PyOpenTracks should create a segment there. So
        there should be 2 segments in this track.
        """
        def import_file(filename):
            with self.mock_db_config:
                parser = GpxParserHandler()
                result = parser.parse(filename)
                self.assertTrue(result.code is Result.OK)
                self.assertTrue(result.track is not None)
                self.assertTrue(result.track.track_points is not None)
                self.assertEqual(len(result.track.track_points), 11)

                trackid = DatabaseHelper.insert(result.track)
                self.assertTrue(trackid is not None)

                DatabaseHelper.bulk_insert(result.track.track_points, trackid)

                tracks = DatabaseHelper.get_tracks()
                self.assertEqual(len(tracks), 1)

                track = tracks[0]
                self.assertEqual(track.name, "For tests")
                self.assertEqual(
                    track.description,
                    "This is a GPX created for tests"
                )
                self.assertEqual(track.activity_type, "road biking")
                self.assertEqual(track._totaltime_ms, 40_000)
                self.assertEqual(track._movingtime_ms, 20_000 + 19_000)
                self.assertEqual(track.gain_elevation_m, 11)
                self.assertIsNone(track.loss_elevation_m)
                self.assertEqual(track._maxhr_bpm, 100)
                self.assertEqual(track._avghr_bpm, 100)
                self.assertEqual(track._avgspeed_mps, track._totaldistance_m / 40)
                self.assertEqual(
                    track._avgmovingspeed_mps,
                    track._totaldistance_m / (20 + 19)
                )

                track_points = DatabaseHelper.get_track_points(track.id)
                self.assertEqual(len(track_points), 11)
                self.assertEqual(track_points[-1].segment, 2)

                return track

        # Import -> Export -> Import.
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_speed_zero_in_trkseg.gpx"
        )
        self._import_export_import(filename, import_file)

    def test_import_gpx_3(self):
        """Test import a simple GPX with 29 track points with a long stopped.

        This gpx file contains 29 points in a trkseg but in the end there
        should be 3 segments because two stops (one of them really long).

        The last stopped spreads for 10 track points (in the same place) so 8
        points are discarded.
        """
        def import_file(filename):
            with self.mock_db_config:
                parser = GpxParserHandler()
                result = parser.parse(filename)
                self.assertTrue(result.code is Result.OK)
                self.assertTrue(result.track is not None)
                self.assertTrue(result.track.track_points is not None)
                self.assertEqual(len(result.track.track_points), 21)

                trackid = DatabaseHelper.insert(result.track)
                self.assertTrue(trackid is not None)

                DatabaseHelper.bulk_insert(result.track.track_points, trackid)

                tracks = DatabaseHelper.get_tracks()
                self.assertEqual(len(tracks), 1)

                track = tracks[0]
                self.assertEqual(track.name, "For tests")
                self.assertEqual(
                    track.description,
                    "This is a GPX created for tests"
                )
                self.assertEqual(track.activity_type, "road biking")
                self.assertEqual(track._totaltime_ms, 70_000)
                self.assertEqual(track._movingtime_ms, 20_000 + 19_000 + 21_000)
                self.assertEqual(track.gain_elevation_m, 21)
                self.assertIsNone(track.loss_elevation_m)
                self.assertEqual(track._maxhr_bpm, 100)
                self.assertEqual(track._avghr_bpm, 100)
                self.assertEqual(track._avgspeed_mps, track._totaldistance_m / 70)
                self.assertEqual(
                    track._avgmovingspeed_mps,
                    track._totaldistance_m / (20 + 19 + 21)
                )

                track_points = DatabaseHelper.get_track_points(track.id)
                self.assertEqual(len(track_points), 21)
                self.assertEqual(track_points[-1].segment, 3)

                return track

        # Import -> Export -> Import.
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_several_points_stopped.gpx"
        )
        self._import_export_import(filename, import_file)

    def test_import_gpx_4(self):
        """Test import a simple GPX with 19 track points and 3 segments.

        This gpx file contains 19 points in 3 trkseg.
        """
        def import_file(filename):
            with self.mock_db_config:
                parser = GpxParserHandler()
                result = parser.parse(filename)
                self.assertTrue(result.code is Result.OK)
                self.assertTrue(result.track is not None)
                self.assertTrue(result.track.track_points is not None)
                self.assertEqual(len(result.track.track_points), 19)

                trackid = DatabaseHelper.insert(result.track)
                self.assertTrue(trackid is not None)

                DatabaseHelper.bulk_insert(result.track.track_points, trackid)

                tracks = DatabaseHelper.get_tracks()
                self.assertEqual(len(tracks), 1)

                track = tracks[0]
                self.assertEqual(track.name, "For tests")
                self.assertEqual(
                    track.description,
                    "This is a GPX created for tests"
                )
                self.assertEqual(track.activity_type, "road biking")
                self.assertEqual(track._totaltime_ms, 3_620_000)
                self.assertEqual(track._movingtime_ms, 15_000 + 20_000 + 20_000)
                self.assertEqual(track.gain_elevation_m, 19)
                self.assertIsNone(track.loss_elevation_m)
                self.assertEqual(track._maxhr_bpm, 100)
                self.assertEqual(track._avghr_bpm, 100)
                self.assertEqual(
                    track._avgspeed_mps,
                    track._totaldistance_m / 3_620
                )
                self.assertEqual(
                    track._avgmovingspeed_mps,
                    track._totaldistance_m / (15 + 20 + 20)
                )

                track_points = DatabaseHelper.get_track_points(track.id)
                self.assertEqual(len(track_points), 19)
                self.assertEqual(track_points[-1].segment, 3)

                return track

        # Import -> Export -> Import.
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_trkseg.gpx"
        )
        self._import_export_import(filename, import_file)

    def test_import_gpx_error_1(self):
        """Test import gpx malformed: two points with the same time."""
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/malformed_gpx_with_two_points_same_time.gpx"
        )
        parser = GpxParserHandler()
        result = parser.parse(filename)
        self.assertTrue(result.code is Result.ERROR)
