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

from pyopentracks.utils.utils import TimeUtils


class SegmentTrackRecord:
    """
    A SegmentTrackRecord represent a segment track record.
    """

    def __init__(self, *args):
        self._segmenttrackid = args[0] if args else None
        self._ranking = args[1] if args else None
        self._besttime = args[2] if args else None

    @property
    def segmenttrackid(self):
        return self._segmenttrackid

    @property
    def ranking(self):
        return self._ranking

    @property
    def best_time(self):
        return TimeUtils.ms_to_str(self._besttime)
