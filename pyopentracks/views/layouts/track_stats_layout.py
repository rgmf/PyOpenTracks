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
from pyopentracks.views.layouts.track_summary_layout import TrackSummaryLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_layout.ui")
class TrackStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "TrackStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self, track):
        super().__init__()
        self._track = track

    def get_top_widget(self):
        return self._top_widget

    def load_data(self):
        """Load track_stats object into the _main_widget."""
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        summary_layout = TrackSummaryLayout(self._track)
        self._main_widget.attach(summary_layout, 0, 0, 1, 1)
        summary_layout.build()
