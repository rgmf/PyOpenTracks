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
        # segment_points = [
        #     FitSegmentPoint(0, 455582573, -13430747, int(0.0), int(191.0)),
        #     FitSegmentPoint(1, 455584858, -13430222, int(21.0), int(190.0)),
        #     FitSegmentPoint(2, 455587908, -13429417, int(50.0), int(189.0)),
        #     FitSegmentPoint(3, 455589714, -13428943, int(67.0), int(189.0)),
        #     FitSegmentPoint(4, 455592878, -13428111, int(97.0), int(189.0)),
        #     FitSegmentPoint(5, 455594361, -13427681, int(112.0), int(190.0)),
        #     FitSegmentPoint(6, 455595069, -13427502, int(118.0), int(191.0)),
        #     FitSegmentPoint(7, 455596439, -13427207, int(131.0), int(192.0)),
        #     FitSegmentPoint(8, 455597817, -13426884, int(144.0), int(193.0)),
        #     FitSegmentPoint(9, 455598503, -13426723, int(151.0), int(193.0)),
        #     FitSegmentPoint(10, 455599197, -13426570, int(157.0), int(194.0)),
        #     FitSegmentPoint(11, 455601584, -13426060, int(180.0), int(195.0)),
        #     FitSegmentPoint(12, 455604335, -13425409, int(206.0), int(195.0)),
        # ]
        #
        # encoder = FitSegmentEncoder("Nombre", SPORT["cycling"], segment_points)
        # return encoder.end_and_get()

        segment_points = DatabaseHelper.get_segment_points(self._segment.id)
        track_points, start_time_ms = self._info_from_leader()
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

    def _info_from_leader(self):
        """Get from database the best segment.

        Return:
        track_points -- list of track points from track with best time in the segment.
        start_time_ms -- time in milliseconds from the first track point.
        """
        segment_tracks = DatabaseHelper.get_segment_tracks_by_segmentid(self._segment.id, False)
        if segment_tracks:
            track_points = DatabaseHelper.get_track_points(
                trackid=segment_tracks[0].trackid,
                from_trackpoint_id=segment_tracks[0].track_point_id_start,
                to_trackpoint_id=segment_tracks[0].track_point_id_end
            )
            start_time_ms = track_points[0].time_ms
        else:
            track_points = []
            start_time_ms = None
        return track_points, start_time_ms
