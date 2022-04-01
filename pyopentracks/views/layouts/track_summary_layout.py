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

from gi.repository import Gtk, GObject

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import TypeActivityUtils, TrackPointUtils, DistanceUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_summary_layout.ui")
class TrackSummaryLayout(Gtk.Box):
    """Track summary's layout with stats, map and minimal plot.

    It shows:
    - Main stats from the track.
    - Map with track.
    - Plot with altitude and heart rate data.
    """

    __gtype_name__ = "TrackSummaryLayout"

    _info_box: Gtk.Box = Gtk.Template.Child()
    _main_box: Gtk.Box = Gtk.Template.Child()
    _bottom_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self, track):
        super().__init__()
        self._track = track
        self._map_layout = TrackMapLayout()
        self._plot = LinePlot()

        self.get_style_context().add_class("pyot-bg")

    def build(self):
        # Track's icon, name, description, dates and total time
        self._add_info_track(self._track)

        # Add track stats.
        self._info_box.pack_start(TrackSummaryStatsLayout(self._track), False, True, 0)

        # Load boxes where map and plot will be
        self._add_item_to_bottom_box(Gtk.Label(_("Loading Graph...")))

        # Add map to main box
        self._main_box.pack_end(self._map_layout, False, True, 0)

        # Get track points (if needed) to build plots and add them to the map's layout
        if not self._track.track_points:
            ProcessView(self._on_track_points_end, DatabaseHelper.get_track_points, (self._track.id,)).start()
        else:
            self._on_track_points_end(self._track.track_points)

        # Show all
        self._info_box.show_all()

    def _add_info_track(self, track):
        """Adds track information to the Gtk.Box with the information.

        track -- Track object.
        """
        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_homogeneous(False)
        hbox.get_style_context().add_class("pyot-box-with-margin")

        icon = Gtk.Image.new_from_pixbuf(TypeActivityUtils.get_icon_pixbuf(track.category))
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

        # Recorded with
        if not track.recorded_with.is_unknown():
            label = track.recorded_with.software
            label += " " + track.recorded_with.product.model if track.recorded_with.product else ""
            software_label = Gtk.Label(label=_(f"Recorded with: {label}"), xalign=0.0)
            software_label.get_style_context().add_class("pyot-p-small")

            vbox.pack_start(software_label, False, True, 0)

        hbox.pack_start(vbox, False, True, 0)

        self._info_box.pack_start(hbox, False, True, 0)

    def _add_item_to_scrolled_window(self, widget):
        for child in self._scrolled_window.get_children():
            self._scrolled_window.remove(child)
        self._scrolled_window.add(widget)
        self._scrolled_window.show_all()

    def _add_item_to_bottom_box(self, widget):
        for child in self._bottom_box.get_children():
            self._bottom_box.remove(child)
        self._bottom_box.pack_start(widget, True, True, 0)

    def _on_track_points_end(self, track_points):
        """This method is executed when track_points are ready to load map and plot."""
        self._map_layout.add_polyline_from_points(track_points)

        self._plot.add_values(TrackPointUtils.extract_dict_values(track_points, 10))
        self._plot.draw_and_show()
        self._plot.connect(LinePlot.EVENT_X_CURSOR_POS, self._on_position_in_plot)

        self._add_item_to_bottom_box(self._plot.get_canvas())
        self._plot.draw_and_show()

    def _on_position_in_plot(self, distance, location):
        if location and location[0]:
            self._map_layout.set_location_marker(location[0], DistanceUtils.m_to_str(distance * 1000))


class TrackSummaryStatsLayout(Gtk.Grid):
    """A Gtk.Grid with all track's stats."""

    def __init__(self, track, columns=2):
        """Initialize and create the layout.

        Arguments:
        track -- Track's object.
        columns -- number of columns for the grid layout where stats will be shown.
        """
        super().__init__()

        self.set_column_spacing(10)
        self.set_row_spacing(10)
        self.set_column_homogeneous(True)

        self._track = track
        self._columns = columns
        self._left = 0
        self._top = 0

        # Total distance
        self._add_item(self._track.total_distance_label, self._track.total_distance)
        # Total moving time
        self._add_item(self._track.moving_time_label, self._track.moving_time)
        # Avg. moving speed
        self._add_item(self._track.avg_moving_speed_label, self._track.avg_moving_speed)
        # Max. speed
        self._add_item(self._track.max_speed_label, self._track.max_speed)

        if self._track.max_elevation_m is not None or self._track.min_elevation_m is not None:
            # Max. elevation
            self._add_item(self._track.max_elevation_label, self._track.max_elevation)
            # Min. elevation
            self._add_item(self._track.min_elevation_label, self._track.min_elevation)

        if self._track.gain_elevation_m is not None or self._track.loss_elevation_m is not None:
            # Gain. elevation
            self._add_item(self._track.gain_elevation_label, self._track.gain_elevation)
            # Loss elevation
            self._add_item(self._track.loss_elevation_label, self._track.loss_elevation)

        if self._track.max_hr_bpm is not None or self._track.avg_hr_bpm is not None:
            # Max. heart rate
            self._add_item(self._track.max_hr_label, self._track.max_hr)
            # Avg. heart rate
            self._add_item(self._track.avg_hr_label, self._track.avg_hr)

        if self._track.max_cadence_rpm is not None or self._track.avg_cadence_rpm is not None:
            # Max. cadence
            self._add_item(self._track.max_cadence_label, self._track.max_cadence)
            # Avg. cadence
            self._add_item(self._track.avg_cadence_label, self._track.avg_cadence)

    def _position(self):
        left = self._left
        top = self._top

        self._left, self._top = (self._left + 1, self._top) if self._left < self._columns - 1 else (0, self._top + 1)

        return left, top

    def _add_item(self, label_text, value, label_align=0.5, value_align=0.5):
        """Adds a stat item into the Gtk.Grid.

        Arguments:
        label_text -- the text describing the stats value.
        value -- stat's value.
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

        left, top = self._position()
        self.attach(vbox, left=left, top=top, width=1, height=1)
