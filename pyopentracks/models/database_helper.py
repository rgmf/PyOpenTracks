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

from pyopentracks.models.database import Database
from pyopentracks.models.segment import Segment
from pyopentracks.models.segment_point import SegmentPoint
from pyopentracks.tasks.segment_search import SegmentSearch, SegmentTrackSearch


class DatabaseHelper:

    @staticmethod
    def get_track_by_id(id):
        db = Database()
        return db.get_track_by_id(id)

    @staticmethod
    def get_track_points(trackid):
        db = Database()
        return db.get_track_points(trackid)

    @staticmethod
    def get_aggregated_stats(date_from=None, date_to=None):
        db = Database()
        return db.get_aggregated_stats(date_from, date_to)

    @staticmethod
    def get_years():
        db = Database()
        return db.get_years()

    @staticmethod
    def create_segment(name: str, distance: float, gain: int, loss: int, points: list):
        """Creates a segment.

        Arguments:
        name     -- segment's name.
        distance -- segment's distance.
        gain     -- segment's elevation gain.
        loss     -- segment's elevation loss.
        points   -- segment's TrackPoint list

        Return:
        Segment's object and the list of SegmentPoint's object.
        """
        db = Database()
        segment = Segment(None, name, distance, gain, loss)
        segment.id = db.insert(segment)
        segment_points = [ SegmentPoint(None, segment.id, tp.latitude, tp.longitude, tp.altitude) for tp in points ]
        db.bulk_insert(segment_points, segment.id)
        segment_search = SegmentSearch(segment, segment_points)
        segment_search.start()

    @staticmethod
    def insert(model):
        """Inserts the model.

        If model is a Track then executes the task to find segments in it.

        Return:
        the id of the model inserted or None if any error.
        """
        db = Database()
        return db.insert(model)

    @staticmethod
    def bulk_insert(track_points, trackid):
        """Insert all track points to the track identify by trackid.

        Also, it starts task to find segments in the track identify by trackid.

        Return:
        The number of track points inserted.
        """
        db = Database()
        num_trackpoints = db.bulk_insert(track_points, trackid)
        if num_trackpoints > 0:
            segment_track_search = SegmentTrackSearch(trackid)
            segment_track_search.start()
        return num_trackpoints

    @staticmethod
    def get_segment_by_id(id):
        db = Database()
        return db.get_segment_by_id(id)

    @staticmethod
    def get_segment_tracks_by_trackid(trackid):
        db = Database()
        return db.get_segment_tracks_by_trackid(trackid)

    @staticmethod
    def get_segment_tracks():
        """Gets and returns all segmentracks ordered by segmentid.

        Return:
        A list with all segments with segmentracks, like this:
        [
            {
                segment: <segment's object>,
                segmentracks: [<object 1>, ..., <object n>]
            },
            ...

            {
                segment: <segment's object>,
                segmentracks: [<object 1>, ..., <object n>]
            },
        ]
        """
        result_list = []
        db = Database()
        for segment in db.get_segments():
            obj = {
                "segment": segment,
                "segmentracks": []
            }
            for segmentracks in db.get_segment_tracks_by_segmentid(segment.id):
                obj["segmentracks"].append(segmentracks)
            result_list.append(obj)

        return result_list
