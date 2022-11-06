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

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas
)

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.activity import Activity
from pyopentracks.stats.track_activity_stats import TrackActivityStats
from pyopentracks.utils.utils import TrackPointUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.create_segment_layout import CreateSegmentLayout
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.track_map_layout import TrackInteractiveMapLayout
from pyopentracks.views.layouts.activity_summary_layout import TrackActivitySummaryStatsLayout
from pyopentracks.io.proxy.proxy import TrackActivityStatsProxy


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_map_analytic_layout.ui")
class TrackMapAnalyticLayout(Gtk.Box, Layout):
    __gtype_name__ = "TrackMapAnalyticLayout"

    _button_box: Gtk.ButtonBox = Gtk.Template.Child()
    _create_button: Gtk.Button = Gtk.Template.Child()
    _clear_button: Gtk.Button = Gtk.Template.Child()
    _create_box: Gtk.Box = Gtk.Template.Child()
    _create_frame: Gtk.Frame = Gtk.Template.Child()
    _content_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self, activity: Activity, new_segment_created_cb=None):
        """Activity must have the sections with the track points."""
        super().__init__()
        Layout.__init__(self)

        self.get_style_context().add_class("pyot-bg")
        self._activity = activity
        self._stats = None
        self._track_points = []
        self._new_segment_created_cb = new_segment_created_cb
        self._clear_button.set_label(_("Clear segment"))
        self._clear_button.connect("clicked", self._clear_button_clicked)
        self._create_button.set_label(_("Create segment"))
        self._create_button.connect("clicked", self._create_button_clicked)
        self._button_box.hide()

    def set_new_segment_created_cb(self, cb):
        self._new_segment_created_cb = cb

    def build(self):
        self._map_layout = TrackInteractiveMapLayout()
        self._map_layout.connect("segment-selected", self._segment_selected)
        self._map_layout.add_polyline_from_points(self._activity.all_track_points)
        self._content_box.pack_start(self._map_layout, True, True, 0)
        self.show_all()

    def _clear_button_clicked(self, widget):
        self._reset()

    def _reset(self):
        self._create_box.hide()
        self._button_box.hide()
        self._map_layout.reset()
        self._reset_stats()

    def _reset_stats(self):
        for child in self._content_box.get_children():
            if isinstance(child, TrackActivitySummaryStatsLayout) or isinstance(child, FigureCanvas):
                self._content_box.remove(child)

    def _create_button_clicked(self, widget):
        if self._stats is None or self._track_points is None:
            self._reset()
            pyot_logging.get_logger(__name__).error(
                "self._stats and/or self._track_points are None and they should not"
            )
            return

        for child in self._create_frame.get_children():
            self._create_frame.remove(child)

        self._button_box.hide()
        self._create_box.show()

        create_segment = CreateSegmentLayout()
        self._create_frame.add(create_segment)
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

        self._track_points = map_layout.get_segment().track_points

        plot = LinePlot()
        plot.add_values(TrackPointUtils.extract_dict_values(map_layout.get_segment().track_points, 1))
        plot.draw_and_show()

        self._content_box.pack_start(plot.get_canvas(), True, True, 0)

        track_activity_stats = TrackActivityStats()
        track_activity_stats.compute(map_layout.get_segment().track_points)
        self._stats = TrackActivityStatsProxy(track_activity_stats).to_stats()

        self._content_box.pack_start(TrackActivitySummaryStatsLayout(self._stats, self._activity.category, 4), False, False, 0)

        self.show_all()
