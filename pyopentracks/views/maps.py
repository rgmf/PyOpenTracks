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


class TrackMap:
    def __init__(self):
        self._widget = GtkChamplain.Embed()
        self._view = self._widget.get_view()
        self._view.set_property('kinetic-mode', True)
        self._view.set_property('zoom-level', 5)
        self._layer = None
        self._marker = None
        self._init_location_marker()

    def _append_point(self, layer, lat, lon):
        coord = Champlain.Coordinate.new_full(lat, lon)
        layer.add_node(coord)

    def get_widget(self):
        return self._widget

    def add_polyline(self, locations):
        self._locations = locations

        layer = Champlain.PathLayer()
        for loc in locations:
            self._append_point(layer, loc[0], loc[1])
        self._view.add_layer(layer)

        x_coordinates, y_coordinates = zip(*locations)
        # bbox = self._view.get_bounding_box()
        bbox = Champlain.BoundingBox.new()
        bbox.left = min(y_coordinates)
        bbox.right = max(y_coordinates)
        bbox.bottom = min(x_coordinates)
        bbox.top = max(x_coordinates)

        self._view.ensure_visible(bbox, False)
        self._view.set_zoom_level(10)

    def _init_location_marker(self):
        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
        self._marker = Champlain.Label.new_with_text("0 km", "Serif 10", None, orange)
        self._marker.set_use_markup(True)
        self._marker.set_alignment(Pango.Alignment.RIGHT)

        # self._marker = Champlain.Point.new()
        # self._marker.set_color(orange)
        #self._marker.set_location(40.77, -73.98)

        self._layer = Champlain.MarkerLayer()
        self._layer.add_marker(self._marker)
        self._view.add_layer(self._layer)
        self._layer.hide()

    def set_location_marker(self, location_tuple, text):
        self._layer.show()
        self._marker.set_location(location_tuple[0], location_tuple[1])
        self._marker.set_text(text)
