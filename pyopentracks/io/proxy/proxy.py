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
from pyopentracks.io.parser.records import Point, Record
from pyopentracks.models.section import Section
from pyopentracks.models.stats import Stats
from pyopentracks.models.track import Track
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.stats.track_stats import TrackStats


class RecordProxy:

    __slots__ = ("_record")

    def __init__(self, record: Record):
        self._record = record

    def to_track(self) -> Track:
        track = Track(
            None,
            self._record.uuid,
            self._record.name,
            self._record.description,
            self._record.category,
            self._record.recorded_with.id,
            self._record.time,
            None
        )
        track.sections = self.to_sections()

        track_stats = TrackStats()
        track_stats.compute(track.sections)

        track.stats = TrackStatsProxy(track_stats).to_stats()

        return track

    def to_sections(self) -> List[Section]:
        sections: List[Section] = []
        num = 1
        for segment in self._record.segments:
            section = Section(None, "Section " + str(num), None)
            for point in segment.points:
                section.track_points.append(PointProxy(point).to_track_point())
            sections.append(section)
            num += 1
        return sections


class PointProxy:

    __slots__ = ("_point")

    def __init__(self, point: Point):
        self._point = point

    def to_track_point(self):
        return TrackPoint(
            None, None, self._point.longitude, self._point.latitude, 
            self._point.time,  self._point.speed,
            self._point.altitude, self._point.gain, self._point.loss,
            self._point.heart_rate, self._point.cadence,
            self._point.power, self._point.temperature
        )


class TrackStatsProxy:

    __slots__ = "_track_stats"

    def __init__(self, track_stats: TrackStats):
        self._track_stats = track_stats

    def to_stats(self):
        return Stats(
            None,
            self._track_stats.start_time,
            self._track_stats.end_time,
            self._track_stats.total_distance,
            self._track_stats.total_time,
            self._track_stats.moving_time,
            self._track_stats.avg_speed,
            self._track_stats.avg_moving_speed,
            self._track_stats.max_speed,
            self._track_stats.min_elevation,
            self._track_stats.max_elevation,
            self._track_stats.gain_elevation,
            self._track_stats.loss_elevation,
            self._track_stats.max_hr,
            self._track_stats.avg_hr,
            self._track_stats.max_cadence,
            self._track_stats.avg_cadence,
            None,
            None
        )
