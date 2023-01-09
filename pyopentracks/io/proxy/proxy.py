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
from pyopentracks.io.parser.fit.messages import SetType
from pyopentracks.io.parser.records import Point, Record
from pyopentracks.models.set import Set as SetModel
from pyopentracks.models.section import Section
from pyopentracks.models.stats import Stats
from pyopentracks.models.activity import Activity
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.stats.track_activity_stats import TrackActivityStats


class RecordProxy:

    __slots__ = ("_record")

    def __init__(self, record: Record):
        self._record = record

    def to_activity(self) -> Activity:
        activity = Activity(
            None,
            self._record.uuid,
            self._record.name,
            self._record.description,
            self._record.category,
            self._record.recorded_with.id,
            self._record.start_time,
            None
        )
        activity.sections = self.to_sections()
    
        if self._record.type == Record.Type.TRACK:
            activity_stats = TrackActivityStats()
            activity_stats.compute(activity.sections)

            activity.stats = TrackActivityStatsProxy(self._record, activity_stats).to_stats()
        elif self._record.type == Record.Type.SET:
            activity.stats = SetsProxy(self._record).to_stats()

        return activity

    def to_sets(self) -> List[SetModel]:
        sets_model: List[SetModel] = []
        for set in self._record.sets:
            set_model = SetModel()
            set_model.type = set.type
            set_model.result = set.result
            set_model.exercise_category = set.exercise_category
            set_model.weight = set.weight
            set_model.repetitions = set.repetitions
            set_model.avghr = set.avghr
            set_model.maxhr = set.maxhr
            set_model.time = (set.end - set.start) * 1000
            set_model.calories = set.calories
            set_model.temperature = set.temperature
            set_model.difficulty = set.difficulty
            sets_model.append(set_model)
        return sets_model

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


class TrackActivityStatsProxy:

    __slots__ = ("_record", "_track_activity_stats")

    def __init__(self, record: Record, track_activity_stats: TrackActivityStats):
        self._record = record
        self._track_activity_stats = track_activity_stats

    def to_stats(self):
        return Stats(
            None,
            self._track_activity_stats.start_time,
            self._track_activity_stats.end_time,
            self._track_activity_stats.total_distance,
            self._track_activity_stats.total_time,
            self._track_activity_stats.moving_time,
            self._track_activity_stats.avg_speed,
            self._track_activity_stats.avg_moving_speed,
            self._track_activity_stats.max_speed,
            self._track_activity_stats.min_elevation,
            self._track_activity_stats.max_elevation,
            self._track_activity_stats.gain_elevation,
            self._track_activity_stats.loss_elevation,
            self._track_activity_stats.max_hr,
            self._track_activity_stats.avg_hr,
            self._track_activity_stats.max_cadence,
            self._track_activity_stats.avg_cadence,
            None,
            None,
            self._record.min_temperature,
            self._record.max_temperature,
            self._record.avg_temperature,
            self._record.total_calories
        )


class TrackActivityStatsStatsProxy:

    __slots__ = ("_track_activity_stats")

    def __init__(self, track_activity_stats: TrackActivityStats):
        self._track_activity_stats = track_activity_stats

    def to_stats(self):
        return Stats(
            None,
            self._track_activity_stats.start_time,
            self._track_activity_stats.end_time,
            self._track_activity_stats.total_distance,
            self._track_activity_stats.total_time,
            self._track_activity_stats.moving_time,
            self._track_activity_stats.avg_speed,
            self._track_activity_stats.avg_moving_speed,
            self._track_activity_stats.max_speed,
            self._track_activity_stats.min_elevation,
            self._track_activity_stats.max_elevation,
            self._track_activity_stats.gain_elevation,
            self._track_activity_stats.loss_elevation,
            self._track_activity_stats.max_hr,
            self._track_activity_stats.avg_hr,
            self._track_activity_stats.max_cadence,
            self._track_activity_stats.avg_cadence,
            None,
            None,
            self._track_activity_stats.min_temperature,
            self._track_activity_stats.max_temperature,
            self._track_activity_stats.avg_temperature,
            None
        )


class SetsProxy:

    __slots__ = "_record"

    def __init__(self, record: Record):
        self._record = record

    def to_stats(self):
        total_time_ms = (
            self._record.end_time - self._record.start_time 
            if self._record.end_time is not None and self._record.start_time is not None 
            else None
        )
        moving_time_ms = 0
        for set in self._record.sets:
            if set.type == SetType.ACTIVE.value:
                moving_time_ms += ((set.end - set.start) * 1000)

        return Stats(
            None,
            self._record.start_time,
            self._record.end_time,
            None,
            total_time_ms,
            moving_time_ms,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            self._record.maxhr,
            self._record.avghr,
            None,
            None,
            None,
            None,
            self._record.min_temperature,
            self._record.max_temperature,
            self._record.avg_temperature,
            self._record.total_calories
        )
