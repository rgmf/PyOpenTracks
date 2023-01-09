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
from pyopentracks.utils.utils import TypeActivityUtils, TrackPointUtils, DistanceUtils, TimeUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


class ActivitySummaryLayout:
    """Utility class to creates some Gtk widgets useful for common summary layouts."""

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
        icon.set_pixel_size(48)
        hbox.append(icon)

        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)

        name_label = Gtk.Label.new(activity.name)
        name_label.get_style_context().add_class("pyot-h2")
        name_label.set_xalign(0.0)
        name_label.set_wrap(True)

        vbox.append(name_label)

        # Description
        if activity.description:
            desc_label = Gtk.Label.new(activity.description)
            desc_label.get_style_context().add_class("pyot-p-medium")
            desc_label.set_xalign(0.0)
            desc_label.set_wrap(True)
            vbox.append(desc_label)

        # Date and total time
        hbox_date = Gtk.Box(spacing=30, orientation=Gtk.Orientation.HORIZONTAL)
        hbox_date.set_homogeneous(False)

        start_label = Gtk.Label.new(_(f"Start: {activity.start_time}"))
        start_label.get_style_context().add_class("pyot-p-small")
        start_label.set_xalign(0.0)

        if activity.stats:
            end_label = Gtk.Label.new(_(f"End: {activity.stats.end_time}"))
            end_label.get_style_context().add_class("pyot-p-small")
            end_label.set_xalign(0.0)

            total_time_label = Gtk.Label.new(_(f"Total time: {activity.stats.total_time}"))
            total_time_label.get_style_context().add_class("pyot-p-small")
            total_time_label.set_xalign(0.0)

        hbox_date.append(start_label)

        if activity.stats:
            hbox_date.append(end_label)
            hbox_date.append(total_time_label)

        vbox.append(hbox_date)

        # Recorded with
        if not activity.recorded_with.is_unknown():
            label = activity.recorded_with.software
            label += " " + activity.recorded_with.product.model if activity.recorded_with.product else ""
            software_label = Gtk.Label.new(_(f"Recorded with: {label}"))
            software_label.get_style_context().add_class("pyot-p-small")
            software_label.set_xalign(0.0)

            vbox.append(software_label)

        hbox.append(vbox)

        return hbox

class TrackActivitySummaryLayout(Gtk.ScrolledWindow, Layout):
    """Track activity summary's layout with stats, map and minimal plot.

    It shows:
    - Main stats from the activity.
    - Map with the tracks' activity.
    - Plot with altitude and heart rate data.
    """

    def __init__(self, activity: Activity):
        super().__init__()

        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self._top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._top_box.set_vexpand(True)
        self._top_box.set_homogeneous(True)
        self._info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._info_box.set_hexpand(False)
        self._top_box.append(self._info_box)
        self._bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._main_box.append(self._top_box)
        self._main_box.append(self._bottom_box)

        self.set_child(self._main_box)

        self._activity: Activity = activity
        self.get_style_context().add_class("pyot-bg")

        self._map_layout = None
        self._plot = None

    def build(self):
        # Add activity's info.
        self._info_box.append(ActivitySummaryLayout.info_activity(self._activity))

        # Add activity stats.
        if self._activity.stats:
            self._info_box.append(TrackActivitySummaryStatsLayout(self._activity.stats, self._activity.category))
        else:
            self._info_box.append(Gtk.Label.new(_("There are not stats")))

    def post_build(self):
        self._map_layout = TrackMapLayout()
        self._plot = LinePlot()
        if self._activity.stats:
            # Load boxes where map and plot will be
            self._add_item_to_bottom_box(Gtk.Label.new(_("Loading map and graph...")))

            # Add map to main box
            self._map_layout.set_hexpand(True)
            self._top_box.append(self._map_layout)

            # Build plots and the map's layout
            self._load_map_and_plot(self._activity.all_track_points)

    def _add_item_to_scrolled_window(self, widget):
        for child in self._scrolled_window.get_children():
            self._scrolled_window.remove(child)
        self._scrolled_window.add(widget)

    def _add_item_to_bottom_box(self, widget):
        child = self._bottom_box.get_first_child()
        while child is not None:
            self._bottom_box.remove(child)
            child = self._bottom_box.get_first_child()
        self._bottom_box.append(widget)

    def _load_map_and_plot(self, track_points):
        """Load map and plot."""
        self._map_layout.add_polyline_from_points(TrackPointUtils.to_locations(track_points))

        self._plot.add_values(TrackPointUtils.extract_dict_values(track_points, 10))
        self._plot.connect(LinePlot.EVENT_X_CURSOR_POS, self._on_position_in_plot)

        self._add_item_to_bottom_box(self._plot.get_canvas())

    def _on_position_in_plot(self, distance, location):
        if location and location[0]:
            self._map_layout.set_location_marker(location[0], DistanceUtils.m_to_str(distance * 1000))


class SetActivitySummaryLayout(Gtk.ScrolledWindow, Layout):
    """Set activity summary's layout with stats and plots."""

    def __init__(self, activity):
        super().__init__()
        Layout.__init__(self)

        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._main_box.set_hexpand(True)
        self._main_box.set_vexpand(True)
        self._info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._main_box.append(self._info_box)

        self.set_child(self._main_box)

        self._activity: Activity = activity
        self._sets_layout: SetActivitySetsLayout = None

        self.get_style_context().add_class("pyot-bg")

    def add_sets_layout(self, layout):
        self._sets_layout = layout
        return self

    def build(self):
        # Add activity's info.
        self._info_box.append(ActivitySummaryLayout.info_activity(self._activity))

        # Add activity stats.
        if self._activity.stats:
            self._info_box.append(SetActivitySummaryStatsLayout(self._activity.stats, columns=4))
        else:
            self._info_box.append(Gtk.Label.new(_("There are not stats")))

        # Add sets information.
        if self._sets_layout is not None:
            self._sets_layout.build()
            self._main_box.append(self._sets_layout)

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
        self._column = 0
        self._row = 0

    def _position(self):
        column = self._column
        row = self._row

        self._column, self._row = (self._column + 1, self._row) if self._column < self._columns - 1 else (0, self._row + 1)

        return column, row

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

        value = Gtk.Label.new(value)
        value.get_style_context().add_class("pyot-stats-value")
        value.set_xalign(value_align)
        value.set_justify(value_align)

        label = Gtk.Label.new(label_text)
        label.get_style_context().add_class("pyot-stats-header")
        label.set_xalign(label_align)
        label.set_justify(label_align)

        vbox.append(value)
        vbox.append(label)

        column, row = self._position()
        self.attach(vbox, column=column, row=row, width=1, height=1)


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
            self._add_item(stats.max_cadence_label, stats.max_cadence(category))
            # Avg. cadence
            self._add_item(stats.avg_cadence_label, stats.avg_cadence(category))

        if stats.min_temperature_value is not None or stats.max_temperature_value is not None or stats.avg_temperature_value is not None:
            # Min. temperature
            self._add_item(stats.min_temperature_label, stats.min_temperature)
            # Max. temperature
            self._add_item(stats.max_temperature_label, stats.max_temperature)
            # Avg. temperature
            self._add_item(stats.avg_temperature_label, stats.avg_temperature)

        if stats.total_calories_value is not None:
            # Total calories
            self._add_item(stats.total_calories_label, stats.total_calories)


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

        if stats.min_temperature_value is not None or stats.max_temperature_value is not None or stats.avg_temperature_value is not None:
            # Min. temperature
            self._add_item(stats.min_temperature_label, stats.min_temperature)
            # Max. temperature
            self._add_item(stats.max_temperature_label, stats.max_temperature)
            # Avg. temperature
            self._add_item(stats.avg_temperature_label, stats.avg_temperature)

        if stats.total_calories_value is not None:
            # Total calories
            self._add_item(stats.total_calories_label, stats.total_calories)


class SetActivitySetsLayout(Gtk.Grid):
    """Generic Gtk.Grid for sets layout."""

    def __init__(self, sets: List[Set]):
        super().__init__()

        self.set_margin_top(30)
        self.set_margin_bottom(30)
        self.set_margin_start(30)
        self.set_margin_bottom(30)

        self.set_column_spacing(10)
        self.set_row_spacing(10)
        self.set_column_homogeneous(False)

        self._sets = sets
        self._columns = len(self._sets)

        self._row: int = 1

    def build(self):
        raise NotImplementedError

    def _add_header(self, labels: List[str]):
        for idx in range(min(len(labels), self._columns)):
            label = Gtk.Label.new(labels[idx])
            label.get_style_context().add_class("pyot-p-small")
            label.set_justify(0.5)

            self.attach(label, column=idx, row=0, width=1, height=1)

    def _add_row(self, values: List[str]):
        for idx in range(min(len(values), self._columns)):
            label = Gtk.Label.new(values[idx])
            label.get_style_context().add_class("pyot-p-medium")
            label.set_xalign(0.0)
            label.set_justify(0.5)

            box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
            box.get_style_context().add_class("pyot-stats-bg-color")
            box.set_homogeneous(False)
            box.append(label)

            self.attach(box, column=idx, row=self._row, width=1, height=1)
        self._row += 1


class ClimbingSetsLayout(SetActivitySetsLayout):

    def build(self):
        avghrs = any(filter(lambda s: s.avghr is not None, self._sets))
        maxhrs = any(filter(lambda s: s.maxhr is not None, self._sets))
        calories = any(filter(lambda s: s.calories is not None, self._sets))
        temperatures = any(filter(lambda s: s.temperature is not None, self._sets))
        difficulties = any(filter(lambda s: s.difficulty is not None, self._sets))

        labels = ['#', self._sets[0].result_label, self._sets[0].time_label]
        if avghrs:
            labels.append(self._sets[0].avghr_label)
        if maxhrs:
            labels.append(self._sets[0].maxhr_label)
        if calories:
            labels.append(self._sets[0].calories_label)
        if temperatures:
            labels.append(self._sets[0].temperature_label)
        if difficulties:
            labels.append(self._sets[0].difficulty_label)
        labels.append(_("Resting"))

        self._add_header(labels)
        count = 1
        resting_time = 0
        resting_ready = False
        data_ready = False
        for set in self._sets:
            if set.is_resting:
                resting_time += set.time
                resting_ready = True
            else:
                datas = [str(count), set.result_value, set.time_value]
                if avghrs:
                    datas.append(set.avghr_value)
                if maxhrs:
                    datas.append(set.maxhr_value)
                if calories:
                    datas.append(set.calories_value)
                if temperatures:
                    datas.append(set.temperature_value)
                if difficulties:
                    datas.append(set.difficulty_value)
                data_ready = True

            if resting_ready and data_ready:
                datas.append(TimeUtils.ms_to_str(resting_time, True))
                self._add_row(datas)
                resting_time = 0
                resting_ready = False
                data_ready = False
                count += 1

        if resting_ready and data_ready:
            datas.append(TimeUtils.ms_to_str(resting_time, True))
            self._add_row(datas)


class TrainingSetsLayout(SetActivitySetsLayout):
    
    def build(self):
        weights = any(filter(lambda s: s.weight is not None, self._sets))
        avghrs = any(filter(lambda s: s.avghr is not None, self._sets))
        maxhrs = any(filter(lambda s: s.maxhr is not None, self._sets))
        calories = any(filter(lambda s: s.calories is not None, self._sets))
        temperatures = any(filter(lambda s: s.temperature is not None, self._sets))

        labels = [
            '#', self._sets[0].exercise_category_label, self._sets[0].time_label,
            self._sets[0].repetitions_label
        ]
        if weights:
            labels.append(self._sets[0].weight_label)
        if avghrs:
            labels.append(self._sets[0].avghr_label)
        if maxhrs:
            labels.append(self._sets[0].maxhr_label)
        if calories:
            labels.append(self._sets[0].calories_label)
        if temperatures:
            labels.append(self._sets[0].temperature_label)
        labels.append(_("Resting"))

        self._add_header(labels)
        count = 1
        resting_time = 0
        resting_ready = False
        data_ready = False
        for set in self._sets:
            if set.is_resting:
                resting_time += set.time
                resting_ready = True
            else:
                datas = [str(count), set.exercise_category_value, set.time_value, set.repetitions_value]
                if weights:
                    datas.append(set.weight_value)
                if avghrs:
                    datas.append(set.avghr_value)
                if maxhrs:
                    datas.append(set.maxhr_value)
                if calories:
                    datas.append(set.calories_value)
                if temperatures:
                    datas.append(set.temperature_value)
                data_ready = True

            if resting_ready and data_ready:
                datas.append(TimeUtils.ms_to_str(resting_time, True))
                self._add_row(datas)
                resting_time = 0
                resting_ready = False
                data_ready = False
                count += 1

        if resting_ready and data_ready:
            datas.append(TimeUtils.ms_to_str(resting_time, True))
            self._add_row(datas)

