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

from dataclasses import dataclass
from typing import List

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.utils.utils import DateUtils as du
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import StatsUtils as su
from pyopentracks.utils.utils import DistanceUtils as distu
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.graphs import BarsChart
from pyopentracks.views.layouts.calendar_layout import CalendarLayout
from pyopentracks.views.layouts.layout_builder import LayoutBuilder
from pyopentracks.views.layouts.process_view import ProcessView


class AggregatedStats(Gtk.Box):
    """Gtk.VBox with all aggregated stats from all categories (sports)."""

    def __init__(self):
        """Get all aggregated stats from database and builds the Gtk.VBox.

        It uses a ProcessView (thread) to do all its job.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._setup_ui()
        ProcessView(
            self._aggregated_stats_ready,
            DatabaseHelper.get_aggregated_stats,
            None
        ).start()

    def _setup_ui(self):
        self.set_spacing(10)
        self.get_style_context().add_class("pyot-bg")

    def _aggregated_stats_ready(self, aggregated_stats):
        if not aggregated_stats:
            lbl = Gtk.Label.new(_("There are not any aggregated statistics"))
            lbl.set_xalign(0.5)
            lbl.set_yalign(0.0)
            lbl.set_margin_top(20)
            lbl.get_style_context().add_class("pyot-h3")
            self.append(lbl)
            return
        for aggregated in aggregated_stats:
            LayoutBuilder(lambda layout: self.append(layout))\
                    .set_category(aggregated.category)\
                    .set_type(LayoutBuilder.Layouts.SPORT_SUMMARY)\
                    .set_args((aggregated,))\
                    .make()


class AggregatedStatsMonth(Gtk.Box):
    """Gtk.Box with years combo.

    It loads AnalyticMonthsStack when user select a year in the combo box.
    """

    def __init__(self):
        """Get years and initialize the UI."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self._year_list_store = Gtk.ListStore.new([str, str])
        renderer  = Gtk.CellRendererText()
        self._combo_years = Gtk.ComboBox.new_with_model(self._year_list_store)
        self._combo_years.pack_start(renderer, True)
        self._combo_years.add_attribute(renderer, "text", 0)
        self._combo_years.set_vexpand(False)
        self._combo_years.set_valign(Gtk.Align.START)
        self._combo_years.set_margin_top(20)
        self._combo_years.set_margin_bottom(20)
        self._combo_years.set_margin_start(20)
        self._combo_years.set_margin_end(20)

        years = DatabaseHelper.get_years()
        for y in years:
            self._year_list_store.append([str(y), str(y)])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        if years:
            self._months_stack = AnalyticMonthsStack(years[0])
            self.append(self._combo_years)
            self.append(self._months_stack)
        else:
            label = Gtk.Label.new(_("There are not data"))
            label.set_xalign(0.5)
            label.set_yalign(0.0)
            label.set_hexpand(True)
            label.set_margin_top(20)
            label.get_style_context().add_class("pyot-h3")
            self.append(label)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._months_stack)

            year = self._year_list_store[iter_item][1]

            self._months_stack = AnalyticMonthsStack(year)
            self.append(self._months_stack)


class AnalyticMonthsStack(Gtk.Box):
    """Gtk.Box with Gtk.StackSwitcher with months.

    It loads the following data by month (depending the selected month):
    - a calendar with activities per day and total time per week,
    - total distance chart by activity and
    - SummaryMovingSport or SummaryTimeSport layout by activity.
    """

    @dataclass
    class MonthStats:
        month: int
        stats: List[AggregatedStats]

        @property
        def month_name(self):
            return du.get_month_name(self.month)

    def __init__(self, year):
        """Initialize the switcher and load data through ProcessView."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_end(20)

        self._year = year
        self._data = {}

        self._stack_switcher = Gtk.StackSwitcher()
        self._stack_switcher.set_orientation(Gtk.Orientation.VERTICAL)
        self._stack_switcher.set_vexpand(False)
        self._stack_switcher.set_valign(Gtk.Align.START)

        self._stack = Gtk.Stack()
        self._stack.set_margin_start(20)
        self._stack.set_margin_end(20)
        self._stack.connect(
            "notify::visible-child",
            self._visible_child_changed
        )
        self._stack_switcher.set_stack(self._stack)

        self.append(self._stack_switcher)
        self.append(self._stack)

        ProcessView(
            self._on_stack_data_ready, self._data_loading, (year,)
        ).start()

    def _data_loading(self, year):
        data = {}
        for month in range(1, 13):
            date_from = dtu.first_day_ms(int(year), month)
            date_to = dtu.last_day_ms(int(year), month)
            data[str(year) + str(month)] = AnalyticMonthsStack.MonthStats(
                month,
                DatabaseHelper.get_aggregated_stats(
                    date_from=date_from, date_to=date_to
                )
            )
        return data

    def _on_stack_data_ready(self, data: dict):
        self._data = data
        for idx in self._data:
            ms = self._data[idx]
            box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
            box.get_style_context().add_class("pyot-bg")
            self._stack.add_titled(box, str(self._year) + str(ms.month), ms.month_name)
        self._stack.set_visible_child_name(self._year + str(du.get_today().month))

    def _visible_child_changed(self, stack, gparamstring):
        box = self._stack.get_visible_child()
        box.set_vexpand(False)
        box.set_valign(Gtk.Align.START)
        child_name = self._stack.get_visible_child_name()
        if box and box.get_first_child():
            return
        if not child_name or child_name not in self._data:
            return

        ms = self._data[child_name]
        if ms.stats:
            # Calendar.
            box.append(CalendarLayout(int(ms.month), int(self._year)))

            # Month chart for distance's activity and time's activity.
            # For distance's activity it will show total distance per activity.
            # For time's activity it will show total time per activity.
            list_distance = []
            colors_distance = []
            list_time = []
            colors_time = []
            for i in ms.stats:
                if i.total_distance_float is not None:
                    list_distance.append((i.category, i.total_distance_float))
                    colors_distance.append(tau.get_color(i.category))
                elif i.total_moving_time_ms is not None:
                    list_time.append((i.category, i.total_moving_time_ms))
                    colors_time.append(tau.get_color(i.category))
            
            if len(list_distance) > 0:
                chart_distance = BarsChart(
                    results=dict(list_distance),
                    colors=colors_distance,
                    cb_annotate=lambda value: distu.m_to_str(value * 1000)
                )

                chart_box_distance = Gtk.Box()
                chart_box_distance.set_margin_start(10)
                chart_box_distance.set_margin_end(10)
                chart_box_distance.get_style_context().add_class("pyot-stats-bg-color")
                chart_box_distance.append(chart_distance.get_canvas())

                box.append(chart_box_distance)
                chart_distance.draw_and_show()

            if len(list_time) > 0:
                chart_time = BarsChart(
                    results=dict(list_time),
                    colors=colors_time,
                    cb_annotate=lambda value: tu.ms_to_str(value, True)
                )

                chart_box_time = Gtk.Box()
                chart_box_time.set_margin_start(10)
                chart_box_time.set_margin_end(10)
                chart_box_time.get_style_context().add_class("pyot-stats-bg-color")
                chart_box_time.append(chart_time.get_canvas())

                box.append(chart_box_time)
                chart_time.draw_and_show()

            # Aggregated stats for every category.
            for a in ms.stats:
                LayoutBuilder(lambda layout: box.append(layout))\
                    .set_category(a.category)\
                    .set_type(LayoutBuilder.Layouts.SPORT_SUMMARY)\
                    .set_args((a,))\
                    .make()
        else:
            label = Gtk.Label.new(_("There are not stats for this date"))
            label.set_xalign(0.5)
            label.set_yalign(0.0)
            label.get_style_context().add_class("pyot-h3")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            label.set_margin_start(20)
            label.set_margin_end(20)
            box.append(label)


class AggregatedStatsYear(Gtk.Box):
    """Gtk.Box with a combo box with year to load AnalyticTotalsYear."""

    def __init__(self):
        """Load years in the combo box and load last AnalyticTotalsYear."""
        super().__init__()

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_end(20)

        self._year_list_store = Gtk.ListStore.new([str, str])
        renderer = Gtk.CellRendererText()
        self._combo_years = Gtk.ComboBox.new_with_model(self._year_list_store)
        self._combo_years.pack_start(renderer, True)
        self._combo_years.add_attribute(renderer, "text", 0)
        self._combo_years.set_vexpand(False)
        self._combo_years.set_valign(Gtk.Align.START)
        self._combo_years.set_margin_bottom(20)
        self._combo_years.set_margin_start(20)

        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        if years:
            self._year_totals = AnalyticTotalsYear(years[0])
            self.append(self._combo_years)
            self.append(self._year_totals)
        else:
            label = Gtk.Label.new(_("There are not data"))
            label.set_xalign(0.5)
            label.set_yalign(0.0)
            label.set_hexpand(True)
            label.get_style_context().add_class("pyot-h3")
            self.append(label)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._year_totals)

            year = self._year_list_store[iter_item][1]

            self._year_totals = AnalyticTotalsYear(year)
            self.append(self._year_totals)


class AnalyticTotalsYear(Gtk.Box):
    """Gtk.VBox with activities totals stats in a year."""

    def __init__(self, year):
        """Load through a ProcessView the totals for the year.

        Arguments:
        year -- the year of the totals stats.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._year = year
        ProcessView(
            self._ready,
            DatabaseHelper.get_aggregated_stats,
            (dtu.first_day_ms(int(year), 1), dtu.last_day_ms(int(year), 12))
        ).start()

    def _ready(self, aggregated_list):
        if not aggregated_list:
            lbl = Gtk.Label.new(_("There are not activities"))
            lbl.set_yalign(0.5)
            lbl.set_xalign(0.0)
            lbl.get_style_context().add_class("pyot-h3")
            self.append(lbl)
            return
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(50)
        self._build_headers(
            grid,
            _("Sport"),
            _("Activities"),
            _("Activities\nper Month"),
            _("Distance"),
            _("Time"),
            _("Elevation\nGain"),
            _("Heart Rate\nMaximum"),
            _("Heart Rate\nAverage"),
            _("Cadence\nMaximum"),
            _("Cadence\nAverage"),
            _("Speed/Pace\nAverage")
        )
        for i, aggregated in enumerate(aggregated_list):
            box_icon = self._build_icon_box(aggregated.category)
            box_activities = self._build_info_box(aggregated.total_activities)
            box_activities_per_month = self._build_info_box(
                su.avg_per_month(aggregated.total_activities, int(self._year))
            )
            box_distance = self._build_info_box(aggregated.total_distance)
            box_time = self._build_info_box(aggregated.total_short_moving_time)
            box_gain = self._build_info_box(aggregated.total_elevation_gain)
            box_hr_max = self._build_info_box(aggregated.max_heart_rate)
            box_hr_avg = self._build_info_box(aggregated.avg_heart_rate)
            box_cadence_max = self._build_info_box(aggregated.max_cadence)
            box_cadence_avg = self._build_info_box(aggregated.avg_cadence)
            box_speed_pace_avg = self._build_info_box(aggregated.avg_speed)

            grid.attach(box_icon, 0, i + 1, 1, 1)
            grid.attach(box_activities, 1, i + 1, 1, 1)
            grid.attach(box_activities_per_month, 2, i + 1, 1, 1)
            grid.attach(box_distance, 3, i + 1, 1, 1)
            grid.attach(box_time, 4, i + 1, 1, 1)
            grid.attach(box_gain, 5, i + 1, 1, 1)
            grid.attach(box_hr_max, 6, i + 1, 1, 1)
            grid.attach(box_hr_avg, 7, i + 1, 1, 1)
            grid.attach(box_cadence_max, 8, i + 1, 1, 1)
            grid.attach(box_cadence_avg, 9, i + 1, 1, 1)
            grid.attach(box_speed_pace_avg, 10, i + 1, 1, 1)
        self.append(grid)

    def _build_headers(self, grid, *header_labels):
        i = 0
        for i, label in enumerate(header_labels):
            grid.attach(self._build_header_box(label), i, 0, 1, 1)

    def _build_header_box(self, value):
        box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        lbl = Gtk.Label.new(value)
        lbl.set_margin_top(10)
        lbl.set_margin_bottom(10)
        lbl.set_margin_start(10)
        lbl.set_margin_end(10)
        box.append(lbl)
        return box

    def _build_icon_box(self, category):
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        icon = Gtk.Image()
        icon.set_from_pixbuf(tau.get_icon_pixbuf(category))
        icon.set_pixel_size(24)
        icon.set_margin_top(10)
        icon.set_margin_start(10)
        icon.set_margin_end(10)
        lbl = Gtk.Label.new((category if category else _("Unknown")))
        lbl.set_margin_bottom(10)
        lbl.set_margin_start(10)
        lbl.set_margin_end(10)
        box.append(icon)
        box.append(lbl)
        return box

    def _build_info_box(self, value):
        box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        lbl = Gtk.Label.new(str(value))
        lbl.set_margin_top(10)
        lbl.set_margin_bottom(10)
        lbl.set_margin_start(10)
        lbl.set_margin_end(10)
        lbl.get_style_context().add_class("pyot-h3")
        box.append(lbl)
        return box

