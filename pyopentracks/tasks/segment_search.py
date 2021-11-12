"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>

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

import multiprocessing as mp
import numpy as np

from pyopentracks.utils.utils import LocationUtils
from pyopentracks.models.database import Database
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.stats.track_stats import TrackStats
from pyopentracks.models.segment import Segment
from pyopentracks.models.location import Location


class SegmentSearchAbstract(mp.Process):
    def __init__(self):
        super().__init__()

    def _create_segment_track(self, segment: Segment, stats: TrackStats, from_point: SegmentTrack.Point,
                             to_point: SegmentTrack.Point):
        """Creates a segmentrack register into the database and returns the new SegmentTrack's id"""
        segment_track = SegmentTrack.from_points(segment.id, stats, from_point, to_point)
        db = Database()
        return db.insert(segment_track)

    def _get_track_points_between(self, tp1_id, tp2_id):
        db = Database()
        return db.get_track_points_between(tp1_id, tp2_id)

    def _get_tracks_with_near_point_start(self, bbox, trackid=None):
        db = Database()
        return db.get_tracks_with_near_point_start(bbox, trackid)

    def _get_tracks_with_near_point_end(self, bbox, trackid, trackpoint_id_from):
        db = Database()
        return db.get_tracks_with_near_point_end(bbox, trackid, trackpoint_id_from)

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
    """This Process subclass look for segments in a track and add them into segmentracks database table."""

    def __init__(self, trackid):
        """
        Arguments:
        trackid -- Track's id where the Process will look for segments to add them into segmentracks database table.
        """
        super().__init__()
        self._trackid = trackid

    def run(self):
        db = Database()
        segments = db.get_segments()
        if not segments:
            return
        track_points = db.get_track_points(self._trackid)
        if not track_points:
            return

        for segment in segments:
            segment_points = db.get_segment_points(segment.id)
            if not segment_points:
                continue

            bbox = Location(segment_points[0].latitude, segment_points[0].longitude).bounding_box(1.1 * 5.0)
            start_points = self._get_tracks_with_near_point_start(bbox, self._trackid)
            for start_p in start_points:
                bbox = Location(segment_points[-1].latitude, segment_points[-1].longitude).bounding_box(1.1 * 5.0)
                end_p = self._get_tracks_with_near_point_end(bbox, start_p.trackid, start_p.trackpointid)
                if end_p:
                    track_points = self._get_track_points_between(start_p.trackpointid, end_p.trackpointid)

                    frechet = self._linear_frechet(
                        np.array(list(map(lambda sp: [sp.latitude, sp.longitude], segment_points))),
                        np.array(list(map(lambda tp: [tp.latitude, tp.longitude], track_points)))
                    )

                    stats = TrackStats()
                    stats.compute(track_points)

                    threshold = segment.distance_m + (segment.distance_m * 0.0075)
                    if segment.distance_m + threshold >= stats.total_distance >= segment.distance_m - threshold and frechet < segment.distance_m * 0.03:
                        self._create_segment_track(segment, stats, start_p, end_p)


class SegmentSearch(SegmentSearchAbstract):
    """This Process subclass look for the segment in all tracks.

    Also, builds the stats and add the information into segmentracks table.
    """

    SEARCH_RADIO = 10.0

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
        bbox = Location(self._points[0].latitude, self._points[0].longitude).bounding_box(1.1 * SegmentSearch.SEARCH_RADIO)
        start_points = self._get_tracks_with_near_point_start(bbox)
        for start_p in start_points:
            bbox = Location(self._points[-1].latitude, self._points[-1].longitude).bounding_box(1.1 * SegmentSearch.SEARCH_RADIO)
            end_p = self._get_tracks_with_near_point_end(bbox, start_p.trackid, start_p.trackpointid)
            if end_p:
                track_points = self._get_track_points_between(start_p.trackpointid, end_p.trackpointid)

                frechet = self._linear_frechet(
                        np.array(list(map(lambda sp: [sp.latitude, sp.longitude], self._points))),
                        np.array(list(map(lambda tp: [tp.latitude, tp.longitude], track_points)))
                )

                stats = TrackStats()
                stats.compute(track_points)

                threshold = self._segment.distance_m + (self._segment.distance_m * 0.0075)
                if self._segment.distance_m + threshold >= stats.total_distance >= self._segment.distance_m - threshold and frechet < self._segment.distance_m * 0.03:
                    self._create_segment_track(self._segment, stats, start_p, end_p)
