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

import gi
gi.require_version('Champlain', '0.12')
gi.require_version('GtkChamplain', '0.12')
gi.require_version('GtkClutter', '1.0')
from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GtkChamplain, Champlain, Pango, Gtk


class BaseMap(Gtk.VBox):
    """
    Map with libchamplain library with controls to: zoom in/out and change map's source.
    It offers the possility of draw a path line.
    """

    def __init__(self):
        super().__init__()

        self._embed = GtkChamplain.Embed()
        self._view = self._embed.get_view()
        self._view.set_property('kinetic-mode', True)
        self._view.set_property('zoom-level', 5)
        self._view.set_reactive(True)
        self._layer_polyline = Champlain.PathLayer()

        scale = Champlain.Scale()
        scale.connect_view(self._view)
        self._view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)

        bbox = Gtk.HBox(False, 10)
        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_IN)
        button.connect("clicked", self._zoom_in)
        bbox.add(button)

        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_OUT)
        button.connect("clicked", self._zoom_out)
        bbox.add(button)

        combo = Gtk.ComboBox()
        map_source_factory = Champlain.MapSourceFactory.dup_default()
        liststore = Gtk.ListStore(str, str)
        for source in map_source_factory.get_registered():
            liststore.append([source.get_id(), source.get_name()])
        combo.set_model(liststore)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.add_attribute(cell, 'text', 1)
        combo.connect("changed", self._map_source_changed)
        combo.set_active(0)
        bbox.add(combo)

        self._spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self._spinbutton.connect("changed", self._zoom_changed)
        self._view.connect("notify::zoom-level", self._map_zoom_changed)
        self._spinbutton.set_value(12)
        bbox.add(self._spinbutton)

        button = Gtk.Image()
        self._view.connect("notify::state", self._view_state_changed, button)
        bbox.pack_end(button, False, False, 0)

        self.pack_start(bbox, expand=False, fill=False, padding=0)
        self.pack_start(self._embed, expand=False, fill=False, padding=0)

        self._embed.set_size_request(640, 480)

    def _zoom_in(self, widget):
        self._view.zoom_in()

    def _zoom_out(self, widget):
        self._view.zoom_out()

    def _map_source_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        map_source_factory = Champlain.MapSourceFactory.dup_default()
        source = map_source_factory.create_cached_source(id)
        self._view.set_property("map-source", source)

    def _append_point(self, lat, lon):
        coord = Champlain.Coordinate.new_full(lat, lon)
        self._layer_polyline.add_node(coord)

    def _zoom_changed(self, widget):
        self._view.set_property("zoom-level", self._spinbutton.get_value_as_int())

    def _map_zoom_changed(self, widget, value):
        self._spinbutton.set_value(self._view.get_property("zoom-level"))

    def _view_state_changed(self, view, paramspec, image):
        state = view.get_state()
        if state == Champlain.State.LOADING:
            image.set_from_stock(Gtk.STOCK_NETWORK, Gtk.IconSize.BUTTON)
        else:
            image.clear()

    def add_polyline(self, points_tuple):
        """
        Arguments:
        points_tuble -- list of (latitude, longitude) tuples.
        """
        if not points_tuple:
            return

        for point in points_tuple:
            self._append_point(point[0], point[1])
        self._view.add_layer(self._layer_polyline)
        idx = int(len(points_tuple) / 2)
        self._view.center_on(points_tuple[idx][0], points_tuple[idx][1])
        self._view.set_zoom_level(12)
