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

from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import Champlain, GtkChamplain, Pango

from pyopentracks.views.maps.base_map import BaseMap
from pyopentracks.views.maps.map_segment import MapSegment
from pyopentracks.utils.utils import LocationUtils, TrackPointUtils


class TrackMap(BaseMap):
    """
    A TrackMap is a BaseMap with an only polyline and a marker that can be move around the polyline.

    Also, it has the option of select a MapSegment.
    """
    def __init__(self):
        super().__init__()

        self._begin = None
        self._end = None
        self._segment = MapSegment()
        self._view.add_layer(self._segment)

        self._view.connect("button-release-event", self._mouse_click_cb, self._view)
        self._layer_polyline = Champlain.PathLayer()
        self._layer_marker = None
        self._marker = None
        self._init_location_marker()

        self._track_points = []

    def _append_point(self, lat, lon):
        coord = Champlain.Coordinate.new_full(lat, lon)
        self._layer_polyline.add_node(coord)

    def _init_location_marker(self):
        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
        self._marker = Champlain.Label.new_with_text("0 km", "Serif 10", None, orange)
        self._marker.set_use_markup(True)
        self._marker.set_alignment(Pango.Alignment.RIGHT)

        # self._marker = Champlain.Point.new()
        # self._marker.set_color(orange)
        #self._marker.set_location(40.77, -73.98)

        self._layer_marker = Champlain.MarkerLayer()
        self._layer_marker.add_marker(self._marker)
        self._view.add_layer(self._layer_marker)
        self._layer_marker.hide()

    def _mouse_click_cb(self, actor, event, view):
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

    def add_polyline(self, track_points):
        if not track_points:
            return
        self._track_points = track_points

        for tp in track_points:
            self._append_point(tp.latitude, tp.longitude)
        self._view.add_layer(self._layer_polyline)

        x_coordinates, y_coordinates = zip(*TrackPointUtils.to_locations(track_points))
        # bbox = self._view.get_bounding_box()
        bbox = Champlain.BoundingBox.new()
        bbox.left = min(y_coordinates)
        bbox.right = max(y_coordinates)
        bbox.bottom = min(x_coordinates)
        bbox.top = max(x_coordinates)

        self._view.ensure_visible(bbox, False)
        self._view.set_zoom_level(10)

    def set_location_marker(self, location_tuple, text):
        self._layer_marker.show()
        self._marker.set_location(location_tuple[0], location_tuple[1])
        self._marker.set_text(text)

    def get_segment(self):
        return self._segment

    def clear_segment(self):
        self._segment.clear()
