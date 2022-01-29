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
from gi.repository import GObject, Gtk, Champlain, GtkChamplain, Pango


# IMPORTANT: only for reference: not use!!!
class ReferenceMap:

    def __init__(self, points_tuple):
        self.vbox = Gtk.VBox(False, 10)

        embed = GtkChamplain.Embed()

        self.view = embed.get_view()
        self.view.set_reactive(True)

        self.view.set_property('kinetic-mode', True)
        self.view.set_property('zoom-level', 5)

        scale = Champlain.Scale()
        scale.connect_view(self.view)
        self.view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)

        self.path_layer = Champlain.PathLayer()
        for point in points_tuple:
            self.add_node(self.path_layer, point[0], point[1])
        self.view.add_layer(self.path_layer)
        idx = int(len(points_tuple) / 2)
        self.view.center_on(points_tuple[idx][0], points_tuple[idx][1])

        self.layer = self.create_marker_layer(self.view, points_tuple[0][0], points_tuple[0][1])
        self.view.add_layer(self.layer)
        #self.layer.hide_all_markers()

        bbox = Gtk.HBox(False, 10)
        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_IN)
        button.connect("clicked", self.zoom_in)
        bbox.add(button)

        button = Gtk.Button(stock=Gtk.STOCK_ZOOM_OUT)
        button.connect("clicked", self.zoom_out)
        bbox.add(button)

        button = Gtk.ToggleButton(label="Markers")
        button.set_active(False)
        button.connect("toggled", self.toggle_layer)
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
        combo.connect("changed", self.map_source_changed)
        combo.set_active(0)
        bbox.add(combo)

        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(12)
        bbox.add(self.spinbutton)

        button = Gtk.Image()
        self.view.connect("notify::state", self.view_state_changed, button)
        bbox.pack_end(button, False, False, 0)

        self.vbox.pack_start(bbox, expand=False, fill=False, padding=0)
        self.vbox.add(embed)

    def get_vbox(self):
        return self.vbox

    def add_node(self, path_layer, lat, lon):
        coord = Champlain.Coordinate.new_full(lat, lon)
        path_layer.add_node(coord)

    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def toggle_layer(self, widget):
        if widget.get_active():
            self.path_layer.show()
            self.layer.animate_in_all_markers()
        else:
            self.path_layer.hide()
            self.layer.animate_out_all_markers()

    def zoom_changed(self, widget):
        self.view.set_property("zoom-level", self.spinbutton.get_value_as_int())

    def map_source_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        map_source_factory = Champlain.MapSourceFactory.dup_default()
        source = map_source_factory.create_cached_source(id)
        self.view.set_property("map-source", source)

    def map_zoom_changed(self, widget, value):
        self.spinbutton.set_value(self.view.get_property("zoom-level"))

    def view_state_changed(self, view, paramspec, image):
        state = view.get_state()
        if state == Champlain.State.LOADING:
            image.set_from_stock(Gtk.STOCK_NETWORK, Gtk.IconSize.BUTTON)
        else:
            image.clear()

    def marker_button_release_cb(self, actor, event, view):
        if event.button != 1 and event.click_count > 1:
            return False

        print("Montreal was clicked\n")
        return True

    def create_marker_layer(self, view, latitude, longitude):
        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
        layer = Champlain.MarkerLayer()

        marker = Champlain.Label.new_with_text(_("Start"), "Serif 11", None, orange)
        marker.set_use_markup(True)
        marker.set_alignment(Pango.Alignment.RIGHT)
        marker.set_color(orange)

        marker.set_location(latitude, longitude)
        layer.add_marker(marker)
        marker.set_reactive(True)
        marker.connect("button-release-event", self.marker_button_release_cb, view)

        layer.show()
        return layer
