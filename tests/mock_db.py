import unittest
import sqlite3

import os
import sys
import pathlib

pkgdatadir = os.path.join(
    pathlib.Path(__file__).parent.resolve(),
    "../buildir/buildir/testdir/share/pyopentracks/data"
)
sys.path.insert(1, pkgdatadir)

from mock import patch

from pyopentracks.settings import xdg_data_home
from pyopentracks.models.database import Database, config
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.migrations import Migration
from pyopentracks.models.track import Track
from pyopentracks.models.track_point import TrackPoint


class MockDB(unittest.TestCase):
    """Class for mocking the database in tests.

    Extends test classes that need database.
    """

    @classmethod
    def setUpClass(cls):
        """Set up database for tests."""
        cls.testconfig = {
            "database": os.path.join(
                pathlib.Path(__file__).parent.resolve(),
                "testdatabase.db")
        }

        dbpath = cls.testconfig["database"]
        try:
            print("Borrando fichero:", dbpath)
            os.remove(dbpath)
        except OSError as e:
            print(f"Test database {dbpath} couldn't be removed: {e}")

        cls.mock_db_config = patch.dict(config, cls.testconfig)

        with cls.mock_db_config:
            db = Database()
            migration = Migration(db, 1)
            migration._migrate_1()

    @classmethod
    def tearDownClass(cls):
        """Delete database for tests."""
        dbpath = cls.testconfig["database"]
        try:
            os.remove(dbpath)
        except OSError as e:
            print(f"Test database {dbpath} couldn't be removed: {e}")

    def get_track(self, trackid):
        with self.mock_db_config:
            return DatabaseHelper.get_track_by_id(trackid)

    def get_trackpoints(self, trackid):
        with self.mock_db_config:
            return DatabaseHelper.get_track_points(trackid)

    def update(self, model):
        with self.mock_db_config:
            return DatabaseHelper.update(model)

    def add_track_with_trackpoints(
        self, name="Track", category="biking", num_tp=2, distance_between_tp=10
    ):
        track = Track(
            None, None, name, None, None, category,
            0, num_tp * 10000, num_tp,
            num_tp * 10000, num_tp * 10000, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0
        )

        trackid = None
        with self.mock_db_config:
            trackid = DatabaseHelper.insert(track)

            from_lon_to_lon = 0.0001
            lat = 0
            lon = from_lon_to_lon
            for i in range(num_tp):
                tp = TrackPoint(
                    None, 1, trackid, lon, lat, 0, 0, 0, 0, 0, 0, 0, 0
                )

                lat = min(lat + distance_between_tp / (1852 * 60), 90)
                DatabaseHelper.insert(tp)
        return trackid

