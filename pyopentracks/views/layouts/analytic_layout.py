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

from gi.repository import Gtk

from functools import reduce

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.utils.utils import DateUtils as du
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import StatsUtils as su
from pyopentracks.utils.utils import DistanceUtils as distu
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.graphs import BarsChart
from pyopentracks.views.layouts.calendar_layout import CalendarLayout
from pyopentracks.views.layouts.process_view import ProcessView


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_layout.ui")
class AnalyticLayout(Gtk.Notebook):
    __gtype_name__ = "AnalyticLayout"

    def __init__(self):
        super().__init__()

    def append(self, layout: Gtk.Widget, label: str):
        """Add a new tab to the notebook.

        Every tab contains a scrolled window that contains the layout.

        Arguments:
        layout -- the widget that will contained into the scrolled window.
        label -- the tab's label.
        """
        scrolled_win = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        viewport.add(layout)
        scrolled_win.add(viewport)

        label_widget = Gtk.Label(label)
        self.append_page(scrolled_win, label_widget)
        self.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_summary_sport_layout.ui")
class SummarySport(Gtk.Box):
    __gtype_name__ = "SummarySport"

    _icon: Gtk.Image = Gtk.Template.Child()
    _sport_name: Gtk.Label = Gtk.Template.Child()

    _total_activities: Gtk.Label = Gtk.Template.Child()
    _total_time: Gtk.Label = Gtk.Template.Child()
    _total_moving_time: Gtk.Label = Gtk.Template.Child()
    _total_distance: Gtk.Label = Gtk.Template.Child()
    _total_gain: Gtk.Label = Gtk.Template.Child()

    _avg_time: Gtk.Label = Gtk.Template.Child()
    _avg_moving_time: Gtk.Label = Gtk.Template.Child()
    _avg_distance: Gtk.Label = Gtk.Template.Child()
    _avg_gain: Gtk.Label = Gtk.Template.Child()
    _avg_speed: Gtk.Label = Gtk.Template.Child()
    _avg_speed_label: Gtk.Label = Gtk.Template.Child()
    _avg_heart_rate: Gtk.Label = Gtk.Template.Child()

    _max_time: Gtk.Label = Gtk.Template.Child()
    _max_moving_time: Gtk.Label = Gtk.Template.Child()
    _max_distance: Gtk.Label = Gtk.Template.Child()
    _max_gain: Gtk.Label = Gtk.Template.Child()
    _max_speed: Gtk.Label = Gtk.Template.Child()
    _max_speed_label: Gtk.Label = Gtk.Template.Child()
    _max_heart_rate: Gtk.Label = Gtk.Template.Child()

    def __init__(self, aggregated):
        super().__init__()
        self._icon.set_from_pixbuf(tau.get_icon_pixbuf(aggregated.category))
        self._sport_name.set_label(aggregated.category if aggregated.category else _("Unknown"))
        self._total_activities.set_label(str(aggregated.total_activities))
        self._total_time.set_label(aggregated.total_time)
        self._total_moving_time.set_label(aggregated.total_moving_time)
        self._total_distance.set_label(aggregated.total_distance)
        self._total_gain.set_label(aggregated.total_elevation_gain)
        self._avg_time.set_label(aggregated.avg_time)
        self._avg_moving_time.set_label(aggregated.avg_moving_time)
        self._avg_distance.set_label(aggregated.avg_distance)
        self._avg_gain.set_label(aggregated.avg_elevation_gain)
        self._avg_speed.set_label(aggregated.avg_speed)
        self._avg_speed_label.set_label(aggregated.speed_label)
        self._avg_heart_rate.set_label(aggregated.avg_heart_rate)
        self._max_time.set_label(aggregated.max_time)
        self._max_moving_time.set_label(aggregated.max_moving_time)
        self._max_distance.set_label(aggregated.max_distance)
        self._max_gain.set_label(aggregated.max_elevation_gain)
        self._max_speed.set_label(aggregated.max_speed)
        self._max_speed_label.set_label(aggregated.speed_label)
        self._max_heart_rate.set_label(aggregated.max_heart_rate)
        self.show_all()


class AggregatedStats(Gtk.VBox):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        ProcessView(self._aggregated_stats_ready, DatabaseHelper.get_aggregated_stats, None).start()

    def _setup_ui(self):
        self.set_spacing(10)
        self.get_style_context().add_class("pyot-bg")

    def _aggregated_stats_ready(self, aggregated_stats):
        if not aggregated_stats:
            lbl = Gtk.Label(label=_("There are not any aggregated statistics"))
            lbl.set_yalign(0.0)
            lbl.get_style_context().add_class("pyot-h1")
            self.pack_start(lbl, False, False, 0)
            return
        for aggregated in aggregated_stats:
            self.pack_start(SummarySport(aggregated), False, False, 0)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_month_layout.ui")
class AggregatedStatsMonth(Gtk.Box):
    __gtype_name__ = "AggregatedStatsMonth"

    _combo_years: Gtk.ComboBox = Gtk.Template.Child()
    _year_list_store: Gtk.ListStore = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        self._months_stack = AnalyticMonthsStack(years[0])
        self.pack_start(self._months_stack, False, False, 0)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._months_stack)

            year = self._year_list_store[iter_item][1]

            self._months_stack = AnalyticMonthsStack(year)
            self.pack_start(self._months_stack, False, False, 0)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_months_stack_layout.ui")
class AnalyticMonthsStack(Gtk.Box):
    __gtype_name__ = "AnalyticMonthsStack"

    _stack_switcher: Gtk.StackSwitcher = Gtk.Template.Child()
    _stack: Gtk.Stack = Gtk.Template.Child()

    class Data:
        def __init__(self, al, m, mn):
            self.aggregated_list = al
            self.month = m
            self.month_name = mn

    def __init__(self, year):
        super().__init__()
        self._year = year
        self._data_list = []
        self._stack.connect("notify::visible-child", self._visible_child_changed)
        self._stack_switcher.set_stack(self._stack)
        ProcessView(self._on_stack_data_ready, self._data_loading, (year,)).start()

    def _data_loading(self, year):
        data_list = {}
        month = 1
        for month_name in du.get_months():
            date_from = dtu.first_day_ms(int(year), month)
            date_to = dtu.last_day_ms(int(year), month)
            data_list[str(year) + str(month)] = AnalyticMonthsStack.Data(
                DatabaseHelper.get_aggregated_stats(date_from=date_from, date_to=date_to),
                month,
                month_name
            )
            month = month + 1
        return data_list

    def _on_stack_data_ready(self, data_list):
        self._data_list = data_list
        for idx in self._data_list:
            data = self._data_list[idx]
            month = data.month
            month_name = data.month_name
            box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
            box.get_style_context().add_class("pyot-bg")
            self._stack.add_titled(box, self._year + str(month), month_name)
        self.show_all()

    def _visible_child_changed(self, stack, gparamstring):
        box = self._stack.get_visible_child()
        child_name = self._stack.get_visible_child_name()
        if box and len(box.get_children()) > 0:
            return
        if not child_name or not child_name in self._data_list:
            return

        data = self._data_list[child_name]
        aggregated_list = data.aggregated_list
        if aggregated_list:
            # Calendar.
            box.pack_start(CalendarLayout(int(data.month), int(self._year)), False, False, 0)

            # Month chart.
            list_t = []
            for i in aggregated_list:
                list_t.append((i.category, i.total_distance_float))
            chart = BarsChart(
                results=dict(list_t),
                colors=list(map(lambda a: tau.get_color(a.category), aggregated_list)),
                cb_annotate=lambda value: distu.m_to_str(value * 1000)
            )
            chart_box = Gtk.Box()
            chart_box.set_margin_left(10)
            chart_box.set_margin_right(10)
            chart_box.get_style_context().add_class("pyot-stats-bg-color")
            chart_box.pack_start(chart.get_canvas(), True, True, 10)
            box.pack_start(chart_box, False, False, 0)
            chart_box.show_all()
            chart.draw_and_show()

            # Aggregated stats for every category.
            for a in aggregated_list:
                box.pack_start(SummarySport(a), False, False, 0)
        else:
            label = Gtk.Label(_("There are not stats for this date"))
            label.set_yalign(0.0)
            label.get_style_context().add_class("pyot-h3")
            box.pack_start(label, False, False, 0)
            box.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_year_layout.ui")
class AggregatedStatsYear(Gtk.Box):
    __gtype_name__ = "AggregatedStatsYear"

    _combo_years: Gtk.ComboBox = Gtk.Template.Child()
    _year_list_store: Gtk.ListStore = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        self._year_totals = AnalyticTotalsYear(years[0])
        self.pack_start(self._year_totals, False, False, 0)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._year_totals)

            year = self._year_list_store[iter_item][1]

            self._year_totals = AnalyticTotalsYear(year)
            self.pack_start(self._year_totals, False, False, 0)


class AnalyticTotalsYear(Gtk.VBox):
    def __init__(self, year):
        super().__init__()
        self.get_style_context().add_class(".pru")
        self._year = year
        ProcessView(
            self._ready,
            DatabaseHelper.get_aggregated_stats,
            (dtu.first_day_ms(int(year), 1), dtu.last_day_ms(int(year), 12))
        ).start()

    def _ready(self, aggregated_list):
        if not aggregated_list:
            lbl = Gtk.Label(label=_("There are not activities this year"))
            lbl.set_yalign(0.0)
            lbl.set_xalign(0.0)
            lbl.get_style_context().add_class("pyot-h3")
            self.pack_start(lbl, False, False, 0)
            return
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_left(50)
        self._build_headers(
            grid,
            _("Sport"),
            _("Activities"),
            _("Activities\nper Month"),
            _("Distance"),
            _("Time"),
            _("Elevation\nGain"),
            _("Heart Rate\nMaximum"),
            _("Heart Rate\nAverage")
        )
        for i, aggregated in enumerate(aggregated_list):
            box_icon = self._build_icon_box(aggregated.category)
            box_activities = self._build_info_box(aggregated.total_activities)
            box_activities_per_month = self._build_info_box(su.avg_per_month(aggregated.total_activities, int(self._year)))
            box_distance = self._build_info_box(aggregated.total_distance)
            box_time = self._build_info_box(aggregated.total_short_moving_time)
            box_gain = self._build_info_box(aggregated.total_elevation_gain)
            box_hr_max = self._build_info_box(aggregated.max_heart_rate)
            box_hr_avg = self._build_info_box(aggregated.avg_heart_rate)

            grid.attach(box_icon, 0, i + 1, 1, 1)
            grid.attach(box_activities, 1, i + 1, 1, 1)
            grid.attach(box_activities_per_month, 2, i + 1, 1, 1)
            grid.attach(box_distance, 3, i + 1, 1, 1)
            grid.attach(box_time, 4, i + 1, 1, 1)
            grid.attach(box_gain, 5, i + 1, 1, 1)
            grid.attach(box_hr_max, 6, i + 1, 1, 1)
            grid.attach(box_hr_avg, 7, i + 1, 1, 1)
        self.pack_start(grid, True, True, 10)
        self.show_all()

    def _build_headers(self, grid, *header_labels):
        i = 0
        for i, label in enumerate(header_labels):
            grid.attach(self._build_header_box(label), i, 0, 1, 1)

    def _build_header_box(self, value):
        box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        lbl = Gtk.Label(label=value, xalign=0.5, yalign=0.5)
        box.pack_start(lbl, True, True, 10)
        return box

    def _build_icon_box(self, category):
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        icon = Gtk.Image()
        icon.set_from_pixbuf(tau.get_icon_pixbuf(category))
        lbl = Gtk.Label((category if category else _("Unknown")))
        box.pack_start(icon, False, False, 0)
        box.pack_start(lbl, False, False, 0)
        return box

    def _build_info_box(self, value):
        box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-bg")
        box.set_homogeneous(False)
        lbl = Gtk.Label(label=value, xalign=0.0, yalign=0.5)
        lbl.get_style_context().add_class("pyot-h3")
        box.pack_start(lbl, True, True, 0)
        return box
