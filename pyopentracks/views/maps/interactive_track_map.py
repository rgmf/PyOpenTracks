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

from pyopentracks.views.maps.track_map import TrackMap

from pyopentracks.views.maps.map_segment import MapSegment
from pyopentracks.utils.utils import LocationUtils


class InteractiveTrackMap(TrackMap):
    """A TrackMap with the option of select a MapSegment."""

    def __init__(self):
        super().__init__()

        self._begin = None
        self._end = None
        self._segment = MapSegment()
        self._view.add_layer(self._segment)

        self._view.connect("button-release-event", self._mouse_click_cb, self._view)

    def _mouse_click_cb(self, actor, event, view):
        # Only segments if there are track points, and they are in the database (they're all have id).
        if not self._track_points or not list(filter(lambda tp: tp.id is not None, self._track_points)):
            return False
        x, y = event.x, event.y
        lon, lat = view.x_to_longitude(x), view.y_to_latitude(y)

        filter_tp = list(
            filter(
                lambda tp: LocationUtils.distance_between(tp.latitude, tp.longitude, lat, lon) < 5, self._track_points
            )
        )
        if filter_tp:
            self._segment.add_track_point(filter_tp[0])

        return True

    def get_segment(self):
        return self._segment

    def clear_segment(self):
        self._segment.clear()
        self._view.set_property("zoom-level", 10)
