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

import threading

from gi.repository import Gtk, GLib

from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.maps import TrackMap
from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.views.graphs import LinePlot
from pyopentracks.utils.utils import TrackPointUtils, DistanceUtils
from pyopentracks.models.database import Database


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_layout.ui")
class TrackStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "TrackStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._map = TrackMap()
        self._plot = LinePlot()

    def get_top_widget(self):
        return self._top_widget

    def load_data(self, track):
        """Load track_stats object into the _main_widget.

        Arguments:
        track -- Track object with stats and all information.
        """
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        # Track's icon, name, description, dates and total time
        self._add_info_track(track, 0, 0, 2, 1)
        # Total distance
        self._add_item(track.total_distance_label, track.total_distance, 0, 2, 1, 1)
        # Total moving time
        self._add_item(track.moving_time_label, track.moving_time, 1, 2, 1, 1)
        # Avg. moving speed
        self._add_item(track.avg_moving_speed_label, track.avg_moving_speed, 0, 3, 1, 1)
        # Max. speed
        self._add_item(track.max_speed_label, track.max_speed, 1, 3, 1, 1)
        # Max. elevation
        self._add_item(track.max_elevation_label, track.max_elevation, 0, 4, 1, 1)
        # Min. elevation
        self._add_item(track.min_elevation_label, track.min_elevation, 1, 4, 1, 1)
        # Gain. elevation
        self._add_item(track.gain_elevation_label, track.gain_elevation, 0, 5, 1, 1)
        # Loss elevation
        self._add_item(track.loss_elevation_label, track.loss_elevation, 1, 5, 1, 1)
        # Max. heart rate
        self._add_item(track.max_hr_label, track.max_hr, 0, 6, 1, 1)
        # Avg. heart rate
        self._add_item(track.avg_hr_label, track.avg_hr, 1, 6, 1, 1)

        # Loads boxes where map and plot will be
        self._main_widget.attach(Gtk.Label(_("Loading Map...")), 2, 1, 2, 6)
        self._main_widget.attach(Gtk.Label(_("Loading Graph...")), 0, 7, 4, 24)

        # Show all
        self._main_widget.show_all()

        # Get track points to build map and plots
        db = Database()
        track_points = db.get_track_points(track.id)
        self._on_track_points_end(track_points)

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
        def build(track_points):
            self._map.add_polyline(TrackPointUtils.to_locations(track_points))
            self._plot.add_values(TrackPointUtils.extract_dict_values(track_points, 10))
            self._plot.draw_and_show()
            self._plot.connect(LinePlot.EVENT_X_CURSOR_POS, self._on_position_in_plot)
            GLib.idle_add(self._on_prepare_data_done)
        self._thread = threading.Thread(target=build, args=(track_points,), daemon=True)
        self._thread.start()

    def _on_prepare_data_done(self):
        self._load_map()
        self._load_plot()

    def _load_map(self):
        """Load the map with."""
        self._main_widget.attach(self._map.get_widget(), 2, 1, 2, 6)
        self._map.get_widget().show_all()

    def _load_plot(self):
        self._main_widget.attach(self._plot.get_canvas(), 0, 7, 4, 24)
        self._plot.draw_and_show()

    def _on_position_in_plot(self, distance, location):
        if location and location[0]:
            self._map.set_location_marker(location[0], DistanceUtils.m_to_str(distance * 1000))
