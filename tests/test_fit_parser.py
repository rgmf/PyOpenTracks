import os
import unittest
from pyopentracks.io.parser.exceptions import FitParserException

from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.parser.fit.fit import FitActivity, FitSegment


class TestFitTypeParser(unittest.TestCase):

    def test_activity_type(self):
        """Test FIT activity type"""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/activity.fit"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, FitActivity))

    def test_segment_type(self):
        """Test FIT segment type"""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/segment.fit"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, FitSegment))

        # Parse
        record = parser.parse()
        print()
        print()
        print(record)
        print()
        print()


class TestFitParserActivity(unittest.TestCase):

    def test_activity_type_with_one_segment(self):
        """Test FIT activity with 21 points in one segment"""
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/activity_with_one_segment.fit"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, FitActivity))

        # Parse.
        record = parser.parse()

        self.assertEqual(len(record.segments), 1)
        self.assertEqual(len(record.segments[0].points), 21)

    def test_activity_type_with_two_segments(self):
        """Test FIT activity type with two segments.
        
        In this file there are two stops by events so they will result in 
        two segments:
        - On segment with 12 points.
        - Another one with 7 points.
        """
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/activity_with_two_stop_events.fit"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, FitActivity))

        # Parse.
        record = parser.parse()

        self.assertEqual(len(record.segments), 2)
        self.assertEqual(len(record.segments[0].points), 12)
        self.assertEqual(len(record.segments[1].points), 7)

    def test_activity_type_with_two_segments_speed_0(self):
        """Test FIT activity type with two segments because speed 0.
        
        In this file there are two stops by events so they will result in 
        two segments:
        - On segment with 10 points.
        - Another one with 10 points.
        """
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/activity_with_two_segments_speed_0.fit"
        )

        # Pre-parse.
        parser = ParserFactory.make(filename)

        self.assertTrue(isinstance(parser, FitActivity))

        # Parse.
        record = parser.parse()

        self.assertEqual(len(record.segments), 2)
        self.assertEqual(len(record.segments[0].points), 10)
        self.assertEqual(len(record.segments[1].points), 10)


class TestFitErrorsParse(unittest.TestCase):

    def test_error_course_not_supported_fit_file(self):
        """Test not supported course FIT files"""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/course.fit"
        )

        with self.assertRaises(FitParserException):
            ParserFactory.make(filename)

    def test_error_monitor_not_supported_fit_file(self):
        """Test not supported monitor FIT files"""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/monitor.fit"
        )

        with self.assertRaises(FitParserException):
            ParserFactory.make(filename)

    def test_error_records_not_supported_fit_file(self):
        """Test not supported records FIT files"""

        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/fit/records.fit"
        )

        with self.assertRaises(FitParserException):
            ParserFactory.make(filename)
