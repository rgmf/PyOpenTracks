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
from typing import List

from pyopentracks.libs.fitsegmentencoder.definitions import SPORT, SEGMENT_LEADERBOARD_TYPE
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.libs.fitsegmentencoder.fit_encoder import SegmentPoint as FitSegmentPoint, FitSegmentEncoder, \
    SegmentLeader
from pyopentracks.utils.utils import LocationUtils


class FitSegment:
    def __init__(self, segment, sport: int = None):
        """Class to generate FIT segment binary data.

        Arguments:
        segment -- Segment object.
        sport   -- (optional) one of the SPORT integer values (see pyopentracks.libs.fitsegmentencoder.definitions).
        """
        self._segment = segment
        self._sport = sport

    def compute_binary(self):
        """Compute the segment and return FIT binary segment encoded."""
        segment_points = DatabaseHelper.get_segment_points(self._segment.id)
        track_points = self._track_points_from_leader(len(segment_points))
        start_time_ms = track_points[0] if track_points else None
        last_leader_time = None if start_time_ms is None else int(start_time_ms / 1000)

        fit_segment_points: List[FitSegmentPoint] = []
        last_point = segment_points[0]
        distance_accum = 0
        for idx, sp in enumerate(segment_points):
            latitude, longitude = LocationUtils.degrees_to_semicircles(sp.latitude, sp.longitude)
            last_leader_time = last_leader_time if not track_points or len(track_points) <= idx else int(
                (track_points[idx].time_ms - start_time_ms) / 1000)
            distance_accum += LocationUtils.distance_between(
                last_point.latitude, last_point.longitude, sp.latitude, sp.longitude
                    )
            fit_segment_point = FitSegmentPoint(
                message_index=idx,
                latitude=int(latitude),
                longitude=int(longitude),
                distance=int(distance_accum),
                altitude=int(sp.altitude),
                leader_time=last_leader_time
            )

            fit_segment_points.append(fit_segment_point)
            last_point = sp
        encoder = FitSegmentEncoder(
            name=self._segment.name,
            sport=SPORT["cycling"] if self._sport is None else self._sport,
            segment_points=fit_segment_points
        )
        if last_leader_time is not None:
            encoder.add_leader(
                SegmentLeader(
                    type=SEGMENT_LEADERBOARD_TYPE["personal_best"],
                    segment_time=last_leader_time,
                    name="PR"
                )
            )
        return encoder.end_and_get()

    def _track_points_from_leader(self, max_points: int):
        """Get from database the best segment.

        Arguments:
        max_points -- number of maximum points track_points array will have, so track_points to be returned
                      will be extended or decreased if needed.

        Return:
        track_points -- list of track points from track with best time in the segment.
        """
        track_points = []
        segment_tracks = DatabaseHelper.get_segment_tracks_by_segmentid(self._segment.id, False)
        if segment_tracks:
            track_points = DatabaseHelper.get_track_points(
                trackid=segment_tracks[0].trackid,
                from_trackpoint_id=segment_tracks[0].track_point_id_start,
                to_trackpoint_id=segment_tracks[0].track_point_id_end
            )
            extra = len(track_points) - max_points
            if extra > 0:
                # Decrease track_points to achieve as near as possible max points.
                delete_jump = round(len(track_points) / extra)
                del(track_points[::delete_jump])
            elif extra < 0:
                # Extend track_points repeating items as much as needed to reach nearly max_points.
                repeat = int(max_points / len(track_points))
                track_points = [tp for tp in track_points for _ in range(repeat)]
        return track_points
