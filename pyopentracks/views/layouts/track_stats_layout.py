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

from gi.repository import Gtk, GLib, GObject

from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.maps.track_map import TrackMap
from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.views.graphs import LinePlot
from pyopentracks.utils.utils import TrackPointUtils, DistanceUtils, ElevationUtils
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.stats.track_stats import TrackStats
from pyopentracks.views.layouts.segments_list_layout import SegmentsListLayout
from pyopentracks.views.layouts.process_view import ProcessView


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_layout.ui")
class TrackStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "TrackStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self, track):
        super().__init__()
        self._map = TrackMap()
        self._plot = LinePlot()
        self._track = track

    def get_top_widget(self):
        return self._top_widget

    def load_data(self):
        """Load track_stats object into the _main_widget.
        """
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        # Track's icon, name, description, dates and total time
        self._add_info_track(self._track, 0, 0, 2, 1)
        # Total distance
        self._add_item(self._track.total_distance_label, self._track.total_distance, 0, 2, 1, 1)
        # Total moving time
        self._add_item(self._track.moving_time_label, self._track.moving_time, 1, 2, 1, 1)
        # Avg. moving speed
        self._add_item(self._track.avg_moving_speed_label, self._track.avg_moving_speed, 0, 3, 1, 1)
        # Max. speed
        self._add_item(self._track.max_speed_label, self._track.max_speed, 1, 3, 1, 1)
        # Max. elevation
        self._add_item(self._track.max_elevation_label, self._track.max_elevation, 0, 4, 1, 1)
        # Min. elevation
        self._add_item(self._track.min_elevation_label, self._track.min_elevation, 1, 4, 1, 1)
        # Gain. elevation
        self._add_item(self._track.gain_elevation_label, self._track.gain_elevation, 0, 5, 1, 1)
        # Loss elevation
        self._add_item(self._track.loss_elevation_label, self._track.loss_elevation, 1, 5, 1, 1)
        # Max. heart rate
        self._add_item(self._track.max_hr_label, self._track.max_hr, 0, 6, 1, 1)
        # Avg. heart rate
        self._add_item(self._track.avg_hr_label, self._track.avg_hr, 1, 6, 1, 1)
        # Max. cadence
        self._add_item(self._track.max_cadence_label, self._track.max_cadence, 0, 7, 1, 1)
        # Avg. cadence
        self._add_item(self._track.avg_cadence_label, self._track.avg_cadence, 1, 7, 1, 1)

        # Loads boxes where map and plot will be
        self._main_widget.attach(Gtk.Label(_("Loading Map...")), 2, 1, 2, 7)
        self._main_widget.attach(Gtk.Label(_("Loading Graph...")), 0, 8, 4, 24)

        # Get track points (if needed) to build map and plots
        if not self._track.track_points:
            ProcessView(self._on_track_points_end, DatabaseHelper.get_track_points, (self._track.id,)).start()
        else:
            self._on_track_points_end(self._track.track_points)

        # Load segments.
        segments_list_layout = SegmentsListLayout.from_trackid(self._track.id)
        if segments_list_layout.get_number_rows() > 0:
            self._main_widget.attach(segments_list_layout, 0, 32, 4, 1)

        # Show all
        self._main_widget.show_all()

    def _add_info_track(self, track, left, top, width, height):
        """Adds track information to main widget.

        track -- Track object.
        left -- the column number to attach the left side of item to.
        top -- the row number to attach the top side of item to.
        width --  the number of columns that item will span.
        height -- the number of rows that item will span.
        """
        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_homogeneous(False)
        hbox.get_style_context().add_class("pyot-box-with-margin")

        icon = Gtk.Image.new_from_pixbuf(
            tau.get_icon_pixbuf(track.activity_type)
        )
        icon.set_valign(Gtk.Align.START)
        hbox.pack_start(icon, False, True, 0)

        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)

        name_label = Gtk.Label(label=track.name, xalign=0.0)
        name_label.set_line_wrap(True)
        name_label.get_style_context().add_class("pyot-h2")

        vbox.pack_start(name_label, False, True, 0)

        # Description
        if track.description:
            desc_label = Gtk.Label(label=track.description, xalign=0.0)
            desc_label.set_line_wrap(True)
            desc_label.get_style_context().add_class("pyot-p-medium")
            vbox.pack_start(desc_label, False, True, 0)

        # Date and total time
        hbox_date = Gtk.Box(spacing=30, orientation=Gtk.Orientation.HORIZONTAL)
        hbox_date.set_homogeneous(False)

        start_label = Gtk.Label(label=_(f"Start: {track.start_time}"), xalign=0.0)
        start_label.get_style_context().add_class("pyot-p-small")

        end_label = Gtk.Label(label=_(f"End: {track.end_time}"), xalign=0.0)
        end_label.get_style_context().add_class("pyot-p-small")

        total_time_label = Gtk.Label(label=_(f"Total time: {track.total_time}"), xalign=0.0)
        total_time_label.get_style_context().add_class("pyot-p-small")

        hbox_date.pack_start(start_label, False, True, 0)
        hbox_date.pack_start(end_label, False, True, 0)
        hbox_date.pack_start(total_time_label, False, True, 0)

        vbox.pack_start(hbox_date, False, True, 0)

        hbox.pack_start(vbox, False, True, 0)

        self._main_widget.attach(hbox, left, top, width, height)

    def _add_item(
            self, label_text, value, left, top, width, height,
            label_align=0.5,
            value_align=0.5
    ):
        """Adds an stat item into the _main_widget (Gtk.Grid).

        Arguments:
        label_text -- the text describing the stats value.
        value -- stat's value.
        left -- the column number to attach the left side of item to.
        top -- the row number to attach the top side of item to.
        width --  the number of columns that item will span.
        height -- the number of rows that item will span.
        label_align -- (optional) justify value for label (center by default).
        value_align -- (optional) justify value for value (center by default).
        """
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)

        value = Gtk.Label(label=value, xalign=value_align)
        value.get_style_context().add_class("pyot-stats-value")
        value.set_justify(value_align)

        label = Gtk.Label(label=label_text, xalign=label_align)
        label.get_style_context().add_class("pyot-stats-header")
        label.set_justify(label_align)

        vbox.pack_start(value, True, True, 0)
        vbox.pack_start(label, True, True, 0)

        self._main_widget.attach(vbox, left, top, width, height)

    def _on_track_points_end(self, track_points):
        """This method is executed when track_points are ready to load map and plot."""
        self._map.add_polyline(track_points)
        self._plot.add_values(TrackPointUtils.extract_dict_values(track_points, 10))
        self._plot.draw_and_show()
        self._plot.connect(LinePlot.EVENT_X_CURSOR_POS, self._on_position_in_plot)
        self._load_map()
        self._load_plot()

    def _load_map(self):
        """Load the map with."""
        self._main_widget.attach(self._map, 2, 1, 2, 7)
        self._map.show_all()
        self._map.get_segment().connect("segment-ready", self._segment_ready_cb)

    def _segment_ready_cb(self, segment, trackpoint_begin_id, trackpoint_end_id):
        stats = TrackStats()
        stats.compute(segment._track_points)

        track_stats_segment = self._main_widget.get_child_at(2, 0)
        if not track_stats_segment:
            track_stats_segment = TrackStatsSegmentLayout()
            self._main_widget.attach(track_stats_segment, 2, 0, 2, 1)
            track_stats_segment.connect("destroy", lambda w: self._map.clear_segment())
            track_stats_segment.connect(
                "track-stats-segment-ok",
                lambda w, name, distance, gain, loss:
                DatabaseHelper.create_segment(name, distance, gain, loss, self._map.get_segment().get_track_points())
            )
        track_stats_segment.set_stats(stats)

    def _load_plot(self):
        self._main_widget.attach(self._plot.get_canvas(), 0, 8, 4, 24)
        self._plot.draw_and_show()

    def _on_position_in_plot(self, distance, location):
        if location and location[0]:
            self._map.set_location_marker(location[0], DistanceUtils.m_to_str(distance * 1000))


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_segment_layout.ui")
class TrackStatsSegmentLayout(Gtk.Box, GObject.GObject):
    __gtype_name__ = "TrackStatsSegmentLayout"

    __gsignals__ = {
        "track-stats-segment-ok": (GObject.SIGNAL_RUN_FIRST, None, (str, float, float, float))
    }

    _title_label: Gtk.Label = Gtk.Template.Child()
    _name_entry: Gtk.Entry = Gtk.Template.Child()

    _distance_img: Gtk.Image = Gtk.Template.Child()
    _distance_label: Gtk.Label = Gtk.Template.Child()

    _gain_img: Gtk.Image = Gtk.Template.Child()
    _gain_label: Gtk.Label = Gtk.Template.Child()

    _loss_img: Gtk.Image = Gtk.Template.Child()
    _loss_label: Gtk.Label = Gtk.Template.Child()

    _left_button: Gtk.Button = Gtk.Template.Child()
    _right_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._stats = None

        self._title_label.set_text(_("Create New Segment"))

        self._name_entry.set_placeholder_text(_("Type Segment's Name"))
        self._name_entry.connect("changed", lambda w: self._right_button.set_sensitive(bool(self._name_entry.get_text().strip())))

        self._distance_img.set_from_resource("/es/rgmf/pyopentracks/icons/send-symbolic.svg")
        self._gain_img.set_from_resource("/es/rgmf/pyopentracks/icons/up-symbolic.svg")
        self._loss_img.set_from_resource("/es/rgmf/pyopentracks/icons/down-symbolic.svg")

        self._left_button.set_label(_("Cancel"))
        self._left_button.connect("clicked", lambda btn: self.destroy())

        self._right_button.set_label(_("Create"))
        self._right_button.set_sensitive(False)
        self._right_button.connect("clicked", self._right_button_clicked_cb)

    def _right_button_clicked_cb(self, button):
        self.emit(
            "track-stats-segment-ok",
            self._name_entry.get_text().strip(),
            float(self._stats.total_distance),
            float(self._stats.gain_elevation) if self._stats.gain_elevation else 0,
            float(self._stats.loss_elevation) if self._stats.loss_elevation else 0
        )
        self.destroy()

    def set_stats(self, stats: TrackStats):
        self._stats = stats
        self._distance_label.set_text(DistanceUtils.m_to_str(stats.total_distance))
        self._gain_label.set_text(ElevationUtils.elevation_to_str(stats.gain_elevation))
        self._loss_label.set_text(ElevationUtils.elevation_to_str(stats.loss_elevation))
