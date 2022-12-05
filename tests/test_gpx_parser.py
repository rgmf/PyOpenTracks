from itertools import chain
import os
import unittest
from pyopentracks.io.parser.exceptions import ParserExtensionUnknownException

from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.parser.gpx.gpx import GpxOpenTracks, GpxPath, GpxStandard
from pyopentracks.io.parser.records import Record


class TestGpxStandardParser(unittest.TestCase):

    def test_simple_gpx(self):
        """Test a simple and standard GPX file.
        
        It contains 5 points with only time tag in the same trkseg (segment).
        """

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/standard_simple_file.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, GpxStandard))
        self.assertTrue(isinstance(parser.record, Record))
        
        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)

    def test_with_all_tags_gpx(self):
        """Test an standard GPX file.
        
        It contains 5 points with all tags in the same trkseg (segment).
        """

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/standard_all_tags_file.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, GpxStandard))
        self.assertTrue(isinstance(parser.record, Record))
        
        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.altitude > 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.speed > 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.heart_rate > 0, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)

    def test_with_several_trkseg(self):
        """Test an standard GPX file with several segments.
        
        It contains 5 points in two trkseg (segment).
        """

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/standard_with_two_segments.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxStandard))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 2)
        self.assertEqual(len(parser.record.segments[0].points), 3)
        self.assertEqual(len(parser.record.segments[1].points), 2)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.altitude > 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.speed > 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.heart_rate > 0, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 0)


class TestGpxOpenTracksParser(unittest.TestCase):

    def test_simple_gpx(self):
        """Test a simple OpenTracks GPX file.
        
        It contains 5 points with only time tag in the same trkseg (segment).
        """

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_one_trkseg.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxOpenTracks))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(
            len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, parser.record.segments[0].points))),
            5
        )
        self.assertEqual(
            len(list(filter(lambda o: o.gain >= 0, parser.record.segments[0].points))),
            5
        )
        self.assertEqual(
            len(list(filter(lambda o: o.loss >= 0, parser.record.segments[0].points))),
            5
        )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 1)
        self.assertEqual(len(parser.record.segments[0].points), 5)

    def test_with_several_segments(self):
        """Test an OpenTracks GPX file with several segments."""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_trkseg.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxOpenTracks))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 5)
        self.assertEqual(len(parser.record.segments[2].points), 9)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.gain >= 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.loss >= 0, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 5)
        self.assertEqual(len(parser.record.segments[2].points), 9)

    

    def test_with_several_uncomplet_segments(self):
        """Test an OpenTracks GPX file with several segments.
        
        One of them have not enough points.
        """

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/opentracks_with_trkseg_one_uncomplete.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxOpenTracks))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 3)
        self.assertEqual(len(parser.record.segments[2].points), 9)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.gain >= 0, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.loss >= 0, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 2)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 9)


class TestGpxPathParser(unittest.TestCase):

    def test_simple_gpx(self):
        """Test a GPX file with only points."""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/path_only_points.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxPath))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 5)
        self.assertEqual(len(parser.record.segments[2].points), 9)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 5)
        self.assertEqual(len(parser.record.segments[2].points), 9)

    def test_simple_gpx_one_trkseg_uncomplete(self):
        """Test a GPX file with only points with trkseg one of them uncomplete."""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/path_only_points_trkseg_uncomplete.gpx"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxPath))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "For tests")
        self.assertEqual(parser.record.description, "This is a GPX created for tests")
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 3)
        self.assertEqual(len(parser.record.segments[2].points), 9)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )

        # Parse
        parser.parse()
        self.assertEqual(len(parser.record.segments), 3)
        self.assertEqual(len(parser.record.segments[0].points), 5)
        self.assertEqual(len(parser.record.segments[1].points), 3)
        self.assertEqual(len(parser.record.segments[2].points), 9)

    def test_long_gpx(self):
        """Test a GPX file with 2907 points with locations and elevations."""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/path_long_from_strava.gpx"
        )
        parser = ParserFactory.make(filename)
        
        self.assertTrue(isinstance(parser, GpxPath))
        self.assertTrue(isinstance(parser.record, Record))

        self.assertEqual(parser.record.name, "Long Route")
        self.assertEqual(parser.record.description, "")
        self.assertEqual(len(list(chain(*[ s.points for s in parser.record.segments ]))), 2907)
        for segment in parser.record.segments:
            self.assertEqual(
                len(list(filter(lambda o: o.latitude is not None and o.longitude is not None, segment.points))),
                len(segment.points)
            )
            self.assertEqual(
                len(list(filter(lambda o: o.altitude is not None, segment.points))),
                len(segment.points)
            )


class TestGpxErrorsParser(unittest.TestCase):

    def test_error_extension_not_supported(self):
        """Test extension error."""

        with self.assertRaises(ParserExtensionUnknownException):
            ParserFactory.make("file.not")
