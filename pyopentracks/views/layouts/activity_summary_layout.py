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
from pyopentracks.models.activity import Activity, MultiActivity
from pyopentracks.utils.utils import TypeActivityUtils, TrackPointUtils, DistanceUtils, TimeUtils
from pyopentracks.views.graphs import LinePlot
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


class ActivitySummaryLayout:
    """Utility class to creates some Gtk widgets useful for common summary layouts."""

    @staticmethod
    def info_activity(activity: Activity) -> Gtk.Box:
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
            self._info_box.append(
                TrackActivitySummaryStatsLayout(self._activity.stats, self._activity.category)
            )
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
        if stats.total_distance_m is not None:
            self._add_item(stats.total_distance_label, stats.total_distance)
        # Total moving time
        if stats.moving_time_ms is not None:
            self._add_item(stats.moving_time_label, stats.moving_time)
        # Avg. moving speed
        if stats.avg_moving_speed_mps is not None:
            self._add_item(stats.avg_moving_speed_label(category), stats.avg_moving_speed(category))
        # Max. speed
        if stats.max_speed_mps is not None:
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

        labels = ['#']
        if difficulties:
            labels.append(self._sets[0].difficulty_label)
        labels.append(self._sets[0].result_label)
        labels.append(self._sets[0].time_label)
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
                datas = [str(count)]
                if difficulties:
                    datas.append(set.difficulty_value)
                datas.append(set.result_value)
                datas.append(set.time_value)
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


class MultiActivitySummaryLayout(Gtk.ScrolledWindow, Layout):
    """Multi activity summary's layout."""

    def __init__(self, activity: Activity):
        super().__init__()

        self._activity: Activity = activity
        self.get_style_context().add_class("pyot-bg")
        self.set_vexpand(True)
        self.set_hexpand(True)

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

    def build(self):
        # Add activity's info
        self._info_box.append(ActivitySummaryLayout.info_activity(self._activity))

        # Generic stats from main activity
        if self._activity.stats:
            self._info_box.append(
                TrackActivitySummaryStatsLayout(self._activity.stats, self._activity.category, 3)
            )

        # Multi activity information
        multiactivity = MultiActivity(self._activity)

        header = Gtk.Label.new(_("Sports summary"))
        header.get_style_context().add_class("pyot-h3")
        header.set_xalign(0.0)
        header.set_margin_top(20)
        header.set_margin_start(10)
        header.set_margin_end(10)
        self._info_box.append(header)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(True)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        for ma_data in multiactivity.sequence:
            box_item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box_item.set_hexpand(True)

            box_header = self._build_box_header(ma_data)
            box_item.append(box_header)

            body = self._build_body(ma_data)
            if body is not None:
                box_item.append(body)

            box.append(box_item)

        self._info_box.append(box)

    def post_build(self):
        pass

    def _build_box_header(self, data: MultiActivity.Data) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        if data.is_activity:
            box.get_style_context().add_class("pyot-stats-bg-color")

        icon = Gtk.Image.new_from_pixbuf(TypeActivityUtils.get_icon_pixbuf(data.category))
        icon.set_valign(Gtk.Align.START)
        icon.set_pixel_size(24)
        time_lbl = Gtk.Label.new(data.time)
        time_lbl.get_style_context().add_class("pyot-stats-value-medium")
        speed_lbl = Gtk.Label.new(data.speed if data.speed else "")
        speed_lbl.get_style_context().add_class("pyot-stats-value-medium")

        box.append(icon)
        box.append(time_lbl)
        box.append(speed_lbl)

        return box

    def _build_body(self, data: MultiActivity.Data) -> Gtk.Grid:
        if not data.is_activity or not data.value or not data.value.stats:
            return None

        category = data.value.category
        stats = data.value.stats

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        def attach(label: str, value: str, row: int):
            if value is None:
                return row
            label_gtk = Gtk.Label.new(label)
            label_gtk.get_style_context().add_class("pyot-p-small")
            label_gtk.set_xalign(1.0)
            value_gtk = Gtk.Label.new(value)
            value_gtk.get_style_context().add_class("pyot-stats-value-small")
            value_gtk.set_xalign(0.0)
            grid.attach(label_gtk, 0, row, 1, 1)
            grid.attach(value_gtk, 1, row, 1, 1)
            return row + 1

        row = 0
        row = attach(stats.total_distance_label, stats.total_distance, row)
        row = attach(stats.max_speed_label(category), stats.max_speed(category), row)
        row = attach(stats.avg_hr_label, stats.avg_hr, row)
        row = attach(stats.max_hr_label, stats.max_hr, row)
        row = attach(stats.gain_elevation_label, stats.gain_elevation, row)
        row = attach(stats.loss_elevation_label, stats.loss_elevation, row)

        return grid


class DefaultActivitySummaryLayout(Gtk.ScrolledWindow, Layout):
    """A default, with minimal stats, summary's layout."""

    def __init__(self, activity: Activity):
        super().__init__()
        self._activity: Activity = activity
        self.get_style_context().add_class("pyot-bg")
        self.set_hexpand(True)
        self.set_vexpand(True)

    def build(self):
        # Add activity's info.
        self.set_child(ActivitySummaryLayout.info_activity(self._activity))

    def post_build(self):
        pass
