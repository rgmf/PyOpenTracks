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
from dataclasses import dataclass
from typing import List

from gi.repository import Gtk

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import DateUtils as du
from pyopentracks.utils.utils import DistanceUtils as distu
from pyopentracks.utils.utils import StatsUtils as su
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.views.graphs import BarsChart
from pyopentracks.views.layouts.calendar_layout import CalendarLayout
from pyopentracks.views.layouts.layout_builder import LayoutBuilder
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.widgets.graphs_widget import (
    YearlyAggregatedStatsChartBuilder,
    AllTimesAggregatedStatsChartBuilder
)


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

        builder = AllTimesAggregatedStatsChartBuilder(aggregated_stats)
        for aggregated in aggregated_stats:
            widgets_array = []
            if aggregated.total_distance_float is not None:
                builder.set_activity_distance().set_category_filter(aggregated.category).set_total_activities()
                widgets_array.append((_("Total Activities"), builder.build_widget()))

                builder.set_activity_distance().set_category_filter(aggregated.category).set_distance()
                widgets_array.append((_("Distance"), builder.build_widget()))

                builder.set_activity_distance().set_category_filter(aggregated.category).set_moving_time()
                widgets_array.append((_("Moving Time"), builder.build_widget()))
            else:
                builder.set_activity_time().set_category_filter(aggregated.category).set_total_activities()
                widgets_array.append((_("Total Activities"), builder.build_widget()))

                builder.set_activity_time().set_category_filter(aggregated.category).set_moving_time()
                widgets_array.append((_("Moving Time"), builder.build_widget()))

            notebook = self._create_notebook(widgets_array)

            LayoutBuilder(lambda layout: self.append(layout))\
                    .set_category(aggregated.category)\
                    .append_widget(notebook)\
                    .set_type(LayoutBuilder.Layouts.SPORT_SUMMARY)\
                    .set_args((aggregated,))\
                    .make()

    def _create_notebook(self, labels_and_charts):
        notebook = Gtk.Notebook()
        notebook.set_margin_top(20)
        notebook.set_margin_bottom(20)
        notebook.set_margin_start(50)
        notebook.set_margin_end(5)

        for label, chart in labels_and_charts:
            notebook.append_page(chart, Gtk.Label.new(label))
            chart.draw()

        return notebook


class AggregatedStatsMonth(Gtk.Box):
    """Gtk.Box with years combo.

    It loads AnalyticMonthsStack when user select a year in the combo box.
    """

    def __init__(self):
        """Get years and initialize the UI."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self._year_list_store = Gtk.ListStore.new([str, str])
        renderer = Gtk.CellRendererText()
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
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.set_vexpand(False)
        self.set_hexpand(False)

        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_end(20)

        self._year = year
        self._data = {}

        self._stack_switcher = Gtk.StackSwitcher()
        self._stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._stack_switcher.set_vexpand(False)
        self._stack_switcher.set_valign(Gtk.Align.START)

        self._stack = Gtk.Stack()
        self._stack.set_margin_top(20)
        self._stack.set_margin_bottom(20)
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

        builder = YearlyAggregatedStatsChartBuilder(int(self._year))

        aggregated_distance_list = [a for a in aggregated_list if a.total_distance_float is not None]
        if len(aggregated_distance_list) > 0:
            grid_distance = self._create_grid(
                [_("Sport"), _("Activities"), _("Activities\nper Month"), _("Time"), _("Distance"), _("Elevation\nGain"),
                 _("Cadence\nMaximum"), _("Cadence\nAverage"), _("Speed/Pace\nAverage"), _("Heart Rate\nMaximum"),
                 _("Heart Rate\nAverage")],
                aggregated_distance_list,
                True
            )
            self.append(grid_distance)

            self.append(
                self._create_notebook([
                    (_("Total Activities"), builder.set_activity_distance().set_total_activities().set_category_filter().build_widget()),
                    (_("Distance"), builder.set_activity_distance().set_distance().set_category_filter().build_widget()),
                    (_("Moving Time"), builder.set_activity_distance().set_moving_time().set_category_filter().build_widget())
                ])
            )

        aggregated_time_list = [a for a in aggregated_list if a.total_distance_float is None]
        if len(aggregated_time_list) > 0:
            grid_time = self._create_grid(
                [_("Sport"), _("Activities"), _("Activities\nper Month"), _("Time"), _("Heart Rate\nMaximum"),
                 _("Heart Rate\nAverage")],
                aggregated_time_list,
                False
            )
            grid_time.set_margin_top(30)
            self.append(grid_time)

            self.append(
                self._create_notebook([
                    (_("Total Activities"), builder.set_activity_time().set_total_activities().set_category_filter().build_widget()),
                    (_("Moving Time"), builder.set_activity_time().set_moving_time().set_category_filter().build_widget())
                ])
            )

    def _create_notebook(self, labels_and_charts):
        notebook = Gtk.Notebook()
        notebook.set_margin_top(20)
        notebook.set_margin_bottom(20)
        notebook.set_margin_start(50)
        notebook.set_margin_end(5)

        for label, chart in labels_and_charts:
            notebook.append_page(chart, Gtk.Label.new(label))
            chart.draw()

        return notebook

    def _create_grid(self, headers, data_list, with_distance):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(50)

        self._build_headers(grid, _("Distance Activities") if with_distance else _("Time Activities"), *headers)

        for i, aggregated in enumerate(data_list):
            boxes = [
                self._build_icon_box(aggregated.category),
                self._build_info_box(aggregated.total_activities),
                self._build_info_box(su.avg_per_month(aggregated.total_activities, int(self._year))),
                self._build_info_box(aggregated.total_short_moving_time)
            ]
            if with_distance:
                boxes.extend([
                    self._build_info_box(aggregated.total_distance),
                    self._build_info_box(aggregated.total_elevation_gain),
                    self._build_info_box(aggregated.max_cadence),
                    self._build_info_box(aggregated.avg_cadence),
                    self._build_info_box(aggregated.avg_speed)
                ])
            boxes.extend([
                self._build_info_box(aggregated.max_heart_rate),
                self._build_info_box(aggregated.avg_heart_rate)
            ])

            for j, box in enumerate(boxes):
                grid.attach(box, j, i + 2, 1, 1)

        return grid

    def _build_headers(self, grid, header_title, *header_labels):
        box_title = self._build_header_box(header_title)
        grid.attach(box_title, 0, 0, len(header_labels), 1)
        for i, label in enumerate(header_labels):
            grid.attach(self._build_header_box(label), i, 1, 1, 1)

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
