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

from functools import reduce

import multiprocessing as mp
import numpy as np

from pyopentracks.utils.utils import LocationUtils
from pyopentracks.models.database import Database
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.stats.track_activity_stats import TrackActivityStats
from pyopentracks.models.location import Location


class SegmentSearchAbstract(mp.Process):
    SEARCH_RADIO = 10.0
    FRECHET_THRESHOLD = 50.0

    def __init__(self):
        super().__init__()

    def _create_segment_track(self, segment, track_points, from_point, to_point):
        """Creates a segmentrack register into the database and returns the new SegmentTrack's id.

        Arguments:
        segment      -- Segment object.
        track_points -- list of TrackPoint.
        from_point   -- SegmentTrack.Point object.
        to_point     -- SegmentTrack.Point object.
        """
        stats = TrackActivityStats()
        stats.compute(track_points)

        segment_track = SegmentTrack.from_points(segment.id, stats, from_point, to_point)
        db = Database()
        return db.insert(segment_track)

    def _get_track_points_between(self, tp1_id, tp2_id):
        db = Database()
        return db.get_track_points_between(tp1_id, tp2_id)

    def _get_points_near_point_start(self, bbox, activity_id=None):
        # Gets all points inside the bounding box
        db = Database()
        points = db.get_points_near_point_start(bbox, activity_id)

        # Filters points: it gets only one inside the same minute of time
        filtered_points = []
        nearly_points = []
        for point in points:
            if len(nearly_points) == 0:
                nearly_points.append(point)
            elif abs(nearly_points[0].timestamp - point.timestamp) <= 1 * 60 * 1000:
                nearly_points.append(point)
            else:
                filtered_points.append(reduce(lambda a, b: a if a.timestamp > b.timestamp else b, nearly_points))
                nearly_points = []

        # If there are nearly_points then filter them
        if len(nearly_points) > 0:
            filtered_points.append(reduce(lambda a, b: a if a.timestamp > b.timestamp else b, nearly_points))

        return filtered_points

    def _get_points_near_point_end(self, bbox, activity_id, trackpoint_id_from):
        db = Database()
        return db.get_points_near_point_end(bbox, activity_id, trackpoint_id_from)

    def _linear_frechet(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculates the Fréchet distance between two curves: p and q."""
        n_p = p.shape[0]
        n_q = q.shape[0]
        ca = np.zeros((n_p, n_q), dtype=np.float64)

        for i in range(n_p):
            for j in range(n_q):
                d = LocationUtils.distance_between(p[i, 0], p[i, 1], q[j, 0], q[j, 1])

                if i > 0 and j > 0:
                    ca[i, j] = max(min(ca[i - 1, j], ca[i - 1, j - 1], ca[i, j - 1]), d)
                elif i > 0 and j == 0:
                    ca[i, j] = max(ca[i - 1, 0], d)
                elif i == 0 and j > 0:
                    ca[i, j] = max(ca[0, j - 1], d)
                else:
                    ca[i, j] = d
        return ca[n_p - 1, n_q - 1]


class SegmentTrackSearch(SegmentSearchAbstract):
    """This Process subclass look for segments in a track's activity and add them into segmentracks database table."""

    def __init__(self, activity_id):
        """
        Arguments:
        activity_id -- Activity's id where the Process will look for segments to add them into segmentracks database table.
        """
        super().__init__()
        self._activity_id = activity_id

    def run(self):
        db = Database()
        segments = db.get_segments()
        if not segments:
            return
        track_points = db.get_track_points(self._activity_id)
        if not track_points:
            return

        for segment in segments:
            segment_points = db.get_segment_points(segment.id)
            if not segment_points:
                continue

            bbox = Location(segment_points[0].latitude, segment_points[0].longitude).bounding_box(1.1 * SegmentSearchAbstract.SEARCH_RADIO)
            start_points = self._get_points_near_point_start(bbox, self._activity_id)
            for start_p in start_points:
                bbox = Location(segment_points[-1].latitude, segment_points[-1].longitude).bounding_box(1.1 * SegmentSearchAbstract.SEARCH_RADIO)
                end_p = self._get_points_near_point_end(bbox, start_p.activity_id, start_p.trackpoint_id)
                if end_p:
                    track_points = self._get_track_points_between(start_p.trackpoint_id, end_p.trackpoint_id)

                    frechet = self._linear_frechet(
                        np.array(list(map(lambda sp: [sp.latitude, sp.longitude], segment_points))),
                        np.array(list(map(lambda tp: [tp.latitude, tp.longitude], track_points)))
                    )

                    if frechet < SegmentSearchAbstract.FRECHET_THRESHOLD:
                        self._create_segment_track(segment, track_points, start_p, end_p)


class SegmentSearch(SegmentSearchAbstract):
    """This Process subclass look for the segment in all track's activity.

    Also, builds the stats and add the information into segmentracks table.
    """

    def __init__(self, segment, points):
        """
        Arguments:
        segment -- Segment's object.
        points  -- List of segment's points (every segment's point is a SegmentPoint's object).
        """
        super().__init__()
        self._segment = segment
        self._points = points

    def run(self):
        bbox = Location(self._points[0].latitude, self._points[0].longitude).bounding_box(1.1 * SegmentSearchAbstract.SEARCH_RADIO)
        start_points = self._get_points_near_point_start(bbox)
        for start_p in start_points:
            bbox = Location(self._points[-1].latitude, self._points[-1].longitude).bounding_box(1.1 * SegmentSearchAbstract.SEARCH_RADIO)
            end_p = self._get_points_near_point_end(bbox, start_p.activity_id, start_p.trackpoint_id)
            if end_p:
                track_points = self._get_track_points_between(start_p.trackpoint_id, end_p.trackpoint_id)

                frechet = self._linear_frechet(
                        np.array(list(map(lambda sp: [sp.latitude, sp.longitude], self._points))),
                        np.array(list(map(lambda tp: [tp.latitude, tp.longitude], track_points)))
                )

                if frechet < SegmentSearchAbstract.FRECHET_THRESHOLD:
                    self._create_segment_track(self._segment, track_points, start_p, end_p)
