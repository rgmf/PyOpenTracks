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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/activity_stats_layout.ui")
class ActivityStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "ActivityStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self, activity):
        super().__init__()
        Layout.__init__(self)
        self._activity = activity

    def build(self):
        """Load activity_stats object into the _main_widget."""
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        self._main_widget.attach(Gtk.Label(_("Loading data...")), 0, 0, 1, 1)

        LayoutBuilder(self._on_build_layout_done).set_type(LayoutBuilder.Layouts.ACTIVITY_SUMMARY).set_activity(self._activity).make()

    def _on_build_layout_done(self, layout):
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )
        self._main_widget.attach(layout, 0, 0, 1, 1)
