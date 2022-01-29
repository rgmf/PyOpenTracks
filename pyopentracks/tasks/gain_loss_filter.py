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

from enum import Enum, unique

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import LocationUtils


@unique
class DoingStatus(Enum):
    """Reading gain and loss can result in all those status."""

    ON_THE_FLAT = 1,
    CLIMBING = 2,
    DESCENDING = 3


class GainLossFilter:
    """Filter elevation gain and loss to correct errors.

    Every trackpoint can has an elevation gain and an elevation loss in case
    track was recorded with OpenTracks.

    These values can be inaccurate because the barometric sensor on
    smartphones so this class try to delete impossible gain and loss values.
    """

    ACCUM_DISTANCE_THRESHOLD = 50

    def __init__(self, trackid):
        self._trackid = trackid
        self._accum_gain = 0
        self._accum_loss = 0
        self._trackpoints = []

    def run(self):
        self._trackpoints = DatabaseHelper.get_track_points(self._trackid)
        if not self._trackpoints:
            return None

        self._filter_gain_and_loss()
        self._update_stats()
        return DatabaseHelper.get_track_by_id(self._trackid)

    def _filter_gain_and_loss(self):
        last_tp = self._trackpoints[0]
        doing_status = DoingStatus.ON_THE_FLAT
        accum_distance = 0
        gain = 0
        loss = 0
        for tp in self._trackpoints:
            gain += tp.elevation_gain
            loss += tp.elevation_loss
            accum_distance += LocationUtils.distance_between(
                last_tp.latitude, last_tp.longitude, tp.latitude, tp.longitude
            )

            if accum_distance > self.ACCUM_DISTANCE_THRESHOLD:
                if gain > 0 and loss == 0:
                    doing_status = DoingStatus.CLIMBING
                elif loss > 0 and gain == 0:
                    doing_status = DoingStatus.DESCENDING
                else:
                    doing_status = DoingStatus.ON_THE_FLAT
                    gain = 0
                    loss = 0
                accum_distance = 0

            if doing_status is DoingStatus.CLIMBING and loss == 0:
                self._accum_gain += gain
                gain = 0
                loss = 0
            elif doing_status is DoingStatus.DESCENDING and gain == 0:
                self._accum_loss += loss
                gain = 0
                loss = 0

            last_tp = tp
        if gain > 0 and loss == 0:
            self._accum_gain += gain
        elif loss > 0 and gain == 0:
            self._accum_loss += loss

    def _update_stats(self):
        DatabaseHelper.update_stats(
            self._trackid, self._accum_gain, self._accum_loss
        )
