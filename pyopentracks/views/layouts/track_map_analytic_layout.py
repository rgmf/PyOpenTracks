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

from gi.repository import Gtk

from matplotlib.backends.backend_gtk4agg import (
    FigureCanvasGTK4Agg as FigureCanvas
)

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.activity import Activity
from pyopentracks.stats.track_activity_stats import TrackActivityStats
from pyopentracks.utils.utils import TrackPointUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.track_map_layout import TrackInteractiveMapLayout
from pyopentracks.views.layouts.create_segment_layout import CreateSegmentLayout
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.activity_summary_layout import TrackActivitySummaryStatsLayout
from pyopentracks.io.proxy.proxy import TrackActivityStatsStatsProxy


class TrackMapAnalyticLayout(Gtk.Box, Layout):

    def __init__(self, activity: Activity, new_segment_created_cb=None):
        """Activity must have the sections with the track points."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        Layout.__init__(self)

        self.get_style_context().add_class("pyot-bg")

        self._button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._button_box.set_halign(Gtk.Align.END)
        self._button_box.set_margin_top(20)
        self._button_box.set_margin_bottom(20)
        self._button_box.set_margin_start(20)
        self._button_box.set_margin_end(20)
        self._create_button = Gtk.Button.new_with_label(_("Create segment"))
        self._create_button.connect("clicked", self._create_button_clicked)
        self._clear_button = Gtk.Button.new_with_label(_("Discard segment"))
        self._clear_button.connect("clicked", self._clear_button_clicked)
        self._clear_button.set_margin_start(10)
        self._button_box.append(self._create_button)
        self._button_box.append(self._clear_button)

        self._create_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._create_box.set_margin_top(20)
        self._create_box.set_margin_bottom(20)
        self._create_frame = Gtk.Frame()
        self._create_frame.set_halign(Gtk.Align.CENTER)
        self._create_frame.set_hexpand(False)
        self._create_box.append(self._create_frame)

        self._content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.append(self._button_box)
        self.append(self._create_box)
        self.append(self._content_box)

        self._activity = activity
        self._stats = None
        self._track_points = []
        self._new_segment_created_cb = new_segment_created_cb
        self._button_box.hide()

    def set_new_segment_created_cb(self, cb):
        self._new_segment_created_cb = cb

    def build(self):
        self._map_layout = TrackInteractiveMapLayout(self._activity.all_track_points)
        self._map_layout.set_vexpand(True)
        self._map_layout.connect("segment-selected", self._segment_selected)
        self._content_box.append(self._map_layout)

    def _clear_button_clicked(self, widget):
        self._reset()

    def _reset(self):
        self._create_box.hide()
        self._button_box.hide()
        self._map_layout.show()
        self._reset_stats()

    def _reset_stats(self):
        child = self._content_box.get_first_child()
        while child is not None:
            if isinstance(child, TrackActivitySummaryStatsLayout) or isinstance(child, FigureCanvas):
                sibling = child.get_next_sibling()
                self._content_box.remove(child)
                child = sibling
            else:
                child = child.get_next_sibling()

    def _create_button_clicked(self, widget):
        if self._stats is None or self._track_points is None:
            self._reset()
            pyot_logging.get_logger(__name__).error(
                "self._stats and/or self._track_points are None and they should not"
            )
            return

        self._button_box.hide()
        self._create_box.show()

        create_segment = CreateSegmentLayout()
        create_segment.set_margin_top(20)
        create_segment.set_margin_bottom(20)
        create_segment.set_margin_start(20)
        create_segment.set_margin_end(20)
        self._create_frame.set_child(create_segment)
        create_segment.connect("track-activity-stats-segment-cancel", self._cancel_segment)
        create_segment.connect("track-activity-stats-segment-ok", self._create_segment)
        create_segment.set_stats(self._stats)

    def _cancel_segment(self, widget):
        self._button_box.show()
        self._create_box.hide()

    def _create_segment(self, widget, name, distance, gain, loss):
        DatabaseHelper.create_segment(name, distance, gain, loss, self._track_points)
        self._reset()
        if self._new_segment_created_cb is not None:
            self._new_segment_created_cb()

    def _segment_selected(self, map_layout: TrackInteractiveMapLayout, track_point_id_begin: int, track_point_id_end: int):
        self._reset_stats()
        self._button_box.show()

        self._track_points = map_layout.get_selected_track_points()

        plot = LinePlot()
        plot.add_values(TrackPointUtils.extract_dict_values(self._track_points, 1))
        plot.draw_and_show()

        self._content_box.append(plot.get_canvas())

        track_activity_stats = TrackActivityStats()
        track_activity_stats.compute(self._track_points)
        self._stats = TrackActivityStatsStatsProxy(track_activity_stats).to_stats()

        self._content_box.append(TrackActivitySummaryStatsLayout(self._stats, self._activity.category, 4))

        map_layout.hide()

