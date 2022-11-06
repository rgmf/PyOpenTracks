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

from typing import List
from gi.repository import Gtk
from pyopentracks.models.set import Set

from pyopentracks.models.stats import Stats
from pyopentracks.models.activity import Activity
from pyopentracks.utils.utils import TypeActivityUtils, TrackPointUtils, DistanceUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


class ActivitySummaryLayout:
    """Utility class to creates somw Gtk widgets useful for common summary layouts."""

    @staticmethod
    def info_activity(activity: Activity):
        """Creates an Gtk.Box with horizontal orientation with Activity's info.

        Arguments:
            activity -- activity object.
        """
        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_homogeneous(False)
        hbox.get_style_context().add_class("pyot-box-with-margin")

        icon = Gtk.Image.new_from_pixbuf(TypeActivityUtils.get_icon_pixbuf(activity.category))
        icon.set_valign(Gtk.Align.START)
        hbox.pack_start(icon, False, True, 0)

        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)

        name_label = Gtk.Label(label=activity.name, xalign=0.0)
        name_label.set_line_wrap(True)
        name_label.get_style_context().add_class("pyot-h2")

        vbox.pack_start(name_label, False, True, 0)

        # Description
        if activity.description:
            desc_label = Gtk.Label(label=activity.description, xalign=0.0)
            desc_label.set_line_wrap(True)
            desc_label.get_style_context().add_class("pyot-p-medium")
            vbox.pack_start(desc_label, False, True, 0)

        # Date and total time
        hbox_date = Gtk.Box(spacing=30, orientation=Gtk.Orientation.HORIZONTAL)
        hbox_date.set_homogeneous(False)

        start_label = Gtk.Label(label=_(f"Start: {activity.start_time}"), xalign=0.0)
        start_label.get_style_context().add_class("pyot-p-small")

        if activity.stats:
            end_label = Gtk.Label(label=_(f"End: {activity.stats.end_time}"), xalign=0.0)
            end_label.get_style_context().add_class("pyot-p-small")

            total_time_label = Gtk.Label(label=_(f"Total time: {activity.stats.total_time}"), xalign=0.0)
            total_time_label.get_style_context().add_class("pyot-p-small")

        hbox_date.pack_start(start_label, False, True, 0)

        if activity.stats:
            hbox_date.pack_start(end_label, False, True, 0)
            hbox_date.pack_start(total_time_label, False, True, 0)

        vbox.pack_start(hbox_date, False, True, 0)

        # Recorded with
        if not activity.recorded_with.is_unknown():
            label = activity.recorded_with.software
            label += " " + activity.recorded_with.product.model if activity.recorded_with.product else ""
            software_label = Gtk.Label(label=_(f"Recorded with: {label}"), xalign=0.0)
            software_label.get_style_context().add_class("pyot-p-small")

            vbox.pack_start(software_label, False, True, 0)

        hbox.pack_start(vbox, False, True, 0)

        return hbox

@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_activity_summary_layout.ui")
class TrackActivitySummaryLayout(Gtk.Box, Layout):
    """Track activity summary's layout with stats, map and minimal plot.

    It shows:
    - Main stats from the activity.
    - Map with the tracks' activity.
    - Plot with altitude and heart rate data.
    """
    __gtype_name__ = "TrackActivitySummaryLayout"

    _info_box: Gtk.Box = Gtk.Template.Child()
    _main_box: Gtk.Box = Gtk.Template.Child()
    _bottom_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self, activity: Activity):
        super().__init__()

        self._activity: Activity = activity
        self.get_style_context().add_class("pyot-bg")

        self._map_layout = None
        self._plot = None

    def build(self):
        # Add activity's info.
        self._info_box.pack_start(ActivitySummaryLayout.info_activity(self._activity), False, True, 0)

        # Add activity stats.
        if self._activity.stats:
            self._info_box.pack_start(TrackActivitySummaryStatsLayout(self._activity.stats, self._activity.category), False, True, 0)
        else:
            self._info_box.pack_start(Gtk.Label(_("There are not stats")), False, True, 0)

        # Show all
        self._info_box.show_all()

    def post_build(self):
        self._map_layout = TrackMapLayout()
        self._plot = LinePlot()
        if self._activity.stats:
            # Load boxes where map and plot will be
            self._add_item_to_bottom_box(Gtk.Label(_("Loading Graph...")))

            # Add map to main box
            self._main_box.pack_end(self._map_layout, False, True, 0)

            # Build plots and the map's layout
            self._load_map_and_plot(self._activity.all_track_points)

    def _add_item_to_scrolled_window(self, widget):
        for child in self._scrolled_window.get_children():
            self._scrolled_window.remove(child)
        self._scrolled_window.add(widget)
        self._scrolled_window.show_all()

    def _add_item_to_bottom_box(self, widget):
        for child in self._bottom_box.get_children():
            self._bottom_box.remove(child)
        self._bottom_box.pack_start(widget, True, True, 0)

    def _load_map_and_plot(self, track_points):
        """Load map and plot."""
        self._map_layout.add_polyline_from_points(track_points)

        self._plot.add_values(TrackPointUtils.extract_dict_values(track_points, 10))
        self._plot.draw_and_show()
        self._plot.connect(LinePlot.EVENT_X_CURSOR_POS, self._on_position_in_plot)

        self._add_item_to_bottom_box(self._plot.get_canvas())
        self._plot.draw_and_show()

    def _on_position_in_plot(self, distance, location):
        if location and location[0]:
            self._map_layout.set_location_marker(location[0], DistanceUtils.m_to_str(distance * 1000))


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/set_activity_summary_layout.ui")
class SetActivitySummaryLayout(Gtk.Box, Layout):
    """Set activity summary's layout with stats and plots."""

    __gtype_name__ = "SetActivitySummaryLayout"

    _info_box: Gtk.Box = Gtk.Template.Child()
    _main_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self, activity):
        super().__init__()

        self._activity: Activity = activity
        self._sets_layout: SetActivitySetsLayout = None

        self.get_style_context().add_class("pyot-bg")

    def add_sets_layout(self, layout):
        self._sets_layout = layout
        return self

    def build(self):
        # Add activity's info.
        self._info_box.pack_start(ActivitySummaryLayout.info_activity(self._activity), False, True, 0)

        # Add activity stats.
        if self._activity.stats:
            self._info_box.pack_start(SetActivitySummaryStatsLayout(self._activity.stats), False, True, 0)
        else:
            self._info_box.pack_start(Gtk.Label(_("There are not stats")), False, True, 0)

        # Add sets information.
        if self._sets_layout is not None:
            self._sets_layout.build()
            self._main_box.pack_end(self._sets_layout, False, True, 0)

        # Show all
        self.show_all()
        self._info_box.show_all()

    def post_build(self):
        pass


class ActivitySummaryStatsLayout(Gtk.Grid):
    """Generic Gtk.Grid Layout to add stats into boxes."""

    def __init__(self, columns):
        super().__init__()

        self.set_column_spacing(10)
        self.set_row_spacing(10)
        self.set_column_homogeneous(True)

        self._columns = columns
        self._left = 0
        self._top = 0

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


class TrackActivitySummaryStatsLayout(ActivitySummaryStatsLayout):
    """A Gtk.Grid with all track's activity stats."""

    def __init__(self, stats: Stats, category: str, columns=2):
        """Initialize and create the layout.

        Arguments:
            stats -- Stats's object.
            columns -- number of columns for the grid layout where stats will be shown.
        """
        super().__init__(columns)

        # Total distance
        self._add_item(stats.total_distance_label, stats.total_distance)
        # Total moving time
        self._add_item(stats.moving_time_label, stats.moving_time)
        # Avg. moving speed
        self._add_item(stats.avg_moving_speed_label(category), stats.avg_moving_speed(category))
        # Max. speed
        self._add_item(stats.max_speed_label(category), stats.max_speed(category))

        if stats.max_elevation_m is not None or stats.min_elevation_m is not None:
            # Max. elevation
            self._add_item(stats.max_elevation_label, stats.max_elevation)
            # Min. elevation
            self._add_item(stats.min_elevation_label, stats.min_elevation)

        if stats.gain_elevation_m is not None or stats.loss_elevation_m is not None:
            # Gain. elevation
            self._add_item(stats.gain_elevation_label, stats.gain_elevation)
            # Loss elevation
            self._add_item(stats.loss_elevation_label, stats.loss_elevation)

        if stats.max_hr_bpm is not None or stats.avg_hr_bpm is not None:
            # Max. heart rate
            self._add_item(stats.max_hr_label, stats.max_hr)
            # Avg. heart rate
            self._add_item(stats.avg_hr_label, stats.avg_hr)

        if stats.max_cadence_rpm is not None or stats.avg_cadence_rpm is not None:
            # Max. cadence
            self._add_item(stats.max_cadence_label, stats.max_cadence)
            # Avg. cadence
            self._add_item(stats.avg_cadence_label, stats.avg_cadence)


class SetActivitySummaryStatsLayout(ActivitySummaryStatsLayout):
    """A Gtk.Grid with all sets's activity stats."""

    def __init__(self, stats: Stats, columns=2):
        """Initialize and create the layout.

        Arguments:
            stats -- Stats's object.
            columns -- number of columns for the grid layout where stats will be shown.
        """
        super().__init__(columns)

        # Total time
        self._add_item(stats.total_time_label, stats.total_time)
        # Total moving time
        self._add_item(stats.moving_time_label, stats.moving_time)

        if stats.max_hr_bpm is not None or stats.avg_hr_bpm is not None:
            # Max. heart rate
            self._add_item(stats.max_hr_label, stats.max_hr)
            # Avg. heart rate
            self._add_item(stats.avg_hr_label, stats.avg_hr)

        if stats._avg_temperature is not None or stats._max_temperature is not None:
            # Max. temperature
            self._add_item(stats.max_temperature_label, stats.max_temperature)
            # Avg. temperature
            self._add_item(stats.avg_temperature_label, stats.avg_temperature)

        if stats.total_calories is not None:
            # Total calories
            self._add_item(stats.total_calories_label, stats.total_calories)


class SetActivitySetsLayout(Gtk.Grid):
    """Generic Gtk.Grid for sets layout."""

    def __init__(self, sets: List[Set]):
        super().__init__()

        self.set_column_spacing(20)
        self.set_row_spacing(30)
        self.set_column_homogeneous(False)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self._sets = sets
        self._columns = len(self._sets)

        self._row: int = 1

    def build(self):
        raise NotImplementedError

    def _add_header(self, labels: List[str]):
        for idx in range(min(len(labels), self._columns)):
            label = Gtk.Label(label=labels[idx], xalign=0.5)
            label.get_style_context().add_class("pyot-p-small")
            label.set_justify(0.5)

            self.attach(label, left=idx, top=0, width=1, height=1)

    def _add_row(self, values: List[str]):
        for idx in range(min(len(values), self._columns)):
            label = Gtk.Label(label=values[idx], xalign=0)
            label.get_style_context().add_class("pyot-p-medium")
            label.set_justify(0.5)

            self.attach(label, left=idx, top=self._row, width=1, height=1)
        self._row += 1


class ClimbingSetsLayout(SetActivitySetsLayout):

    def build(self):
        self._add_header([
            self._sets[0].type_label,
            self._sets[0].time_label,
            self._sets[0].avghr_label,
            self._sets[0].maxhr_label,
            self._sets[0].calories_label,
            self._sets[0].temperature_label,
            self._sets[0].difficulty_label
        ])
        for set in self._sets:
            self._add_row([
                set.type_value(_("Climbing")),
                set.time_value,
                set.avghr_value,
                set.maxhr_value,
                set.calories_value,
                set.temperature_value,
                set.difficulty_value
            ])


class TrainingSetsLayout(SetActivitySetsLayout):
    
    def build(self):
        self._add_header([
            self._sets[0].type_label,
            self._sets[0].time_label,
            self._sets[0].exercise_category_label,
            self._sets[0].weight_label,
            self._sets[0].repetitions_label,
            self._sets[0].avghr_label,
            self._sets[0].maxhr_label,
            self._sets[0].calories_label,
            self._sets[0].temperature_label
        ])
        for set in self._sets:
            self._add_row([
                set.type_value(),
                set.time_value,
                set.exercise_category_value,
                set.weight_value,
                set.repetitions_value,
                set.avghr_value,
                set.maxhr_value,
                set.calories_value,
                set.temperature_value
            ])
