import unittest
import sys

#pkgdatadir = "/home/roman/workspace/PyOpenTracks/buildir/buildir/testdir/share/pyopentracks/data"
#sys.path.insert(1, pkgdatadir)

from pyopentracks.utils.utils import StatsUtils

class TestUtils(unittest.TestCase):
    def test_avg_per_month(self):
        self.assertEqual(StatsUtils.avg_per_month(12, 2008), 1.0)


if __name__ == "__main__":
    unittest.main()
