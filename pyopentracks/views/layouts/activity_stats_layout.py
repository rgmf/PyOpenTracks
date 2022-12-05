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

from gi.repository import Gtk

from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.layout_builder import LayoutBuilder


class ActivityStatsLayout(Gtk.ScrolledWindow, Layout):

    def __init__(self, activity):
        super().__init__()
        Layout.__init__(self)

        self._parent_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._top_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._main_widget = Gtk.Grid()
        self._bottom_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._parent_box.append(self._top_widget)
        self._parent_box.append(self._main_widget)
        self._parent_box.append(self._bottom_widget)
        self.set_child(self._parent_box)

        self._activity = activity

    def build(self):
        """Load activity_stats object into the _main_widget."""
        child = self._main_widget.get_first_child()
        while child is not None:
            self._main_widget.remove(child)
            child = self._main_widget.get_first_child()

        self._main_widget.attach(Gtk.Label.new(_("Loading data...")), 0, 0, 1, 1)

        LayoutBuilder(self._on_build_layout_done).set_type(LayoutBuilder.Layouts.ACTIVITY_SUMMARY).set_activity(self._activity).make()

    def _on_build_layout_done(self, layout):
        child = self._main_widget.get_first_child()
        while child is not None:
            self._main_widget.remove(child)
            child = self._main_widget.get_first_child()
        self._main_widget.attach(layout, 0, 0, 1, 1)
