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
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.graphs import BarsChart
from pyopentracks.views.layouts.calendar_layout import CalendarLayout
from pyopentracks.views.layouts.process_view import ProcessView


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_summary_sport_layout.ui")
class SummarySport(Gtk.Box):
    """Gtk.Box with total, averages and maximum stats for a sport.

    From AggregatedStats model builds a layout with totals, averages and
    maximums stats.
    """

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
        """Fill Gtk.Box with the AggregatedStats model (aggregated)."""
        super().__init__()
        self._icon.set_from_pixbuf(tau.get_icon_pixbuf(aggregated.category))
        self._sport_name.set_label(
            aggregated.category if aggregated.category else _("Unknown")
        )
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
            lbl = Gtk.Label(label=_("There are not any aggregated statistics"))
            lbl.set_yalign(0.0)
            lbl.get_style_context().add_class("pyot-h3")
            self.pack_start(lbl, False, False, 0)
            self.show_all()
            return
        for aggregated in aggregated_stats:
            self.pack_start(SummarySport(aggregated), False, False, 0)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_month_layout.ui")
class AggregatedStatsMonth(Gtk.Box):
    """Gtk.Box with years combo.

    It loads AnalyticMonthsStack when user select a year in the combo box.
    """

    __gtype_name__ = "AggregatedStatsMonth"

    _combo_years: Gtk.ComboBox = Gtk.Template.Child()
    _year_list_store: Gtk.ListStore = Gtk.Template.Child()

    def __init__(self):
        """Get years and initialize the UI."""
        super().__init__()
        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        if years:
            self._months_stack = AnalyticMonthsStack(years[0])
            self.pack_start(self._months_stack, False, False, 0)
        else:
            label = Gtk.Label(_("There are not data"))
            label.get_style_context().add_class("pyot-h3")
            self.pack_start(label, False, False, 50)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._months_stack)

            year = self._year_list_store[iter_item][1]

            self._months_stack = AnalyticMonthsStack(year)
            self.pack_start(self._months_stack, False, False, 0)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_months_stack_layout.ui")
class AnalyticMonthsStack(Gtk.Box):
    """Gtk.Box with Gtk.StackSwitcher with months.

    It loads the following data by month (depending the selected month):
    - a calendar with activities per day and total time per week,
    - total distance chart by activity and
    - SummarySport layout by activity.
    """

    __gtype_name__ = "AnalyticMonthsStack"

    _stack_switcher: Gtk.StackSwitcher = Gtk.Template.Child()
    _stack: Gtk.Stack = Gtk.Template.Child()

    @dataclass
    class MonthStats:
        month: int
        stats: List[AggregatedStats]

        @property
        def month_name(self):
            return du.get_month_name(self.month)

    def __init__(self, year):
        """Initialize the switcher and load data through ProcessView."""
        super().__init__()
        self._year = year
        self._data = {}
        self._stack.connect(
            "notify::visible-child",
            self._visible_child_changed
        )
        self._stack_switcher.set_stack(self._stack)
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
            self._stack.add_titled(box, self._year + str(ms.month), ms.month_name)
        self.show_all()
        self._stack.set_visible_child_name(self._year + str(du.get_today().month))

    def _visible_child_changed(self, stack, gparamstring):
        box = self._stack.get_visible_child()
        child_name = self._stack.get_visible_child_name()
        if box and len(box.get_children()) > 0:
            return
        if not child_name or child_name not in self._data:
            return

        ms = self._data[child_name]
        if ms.stats:
            # Calendar.
            box.pack_start(
                CalendarLayout(int(ms.month), int(self._year)),
                False,
                False,
                0
            )

            # Month chart.
            list_t = []
            for i in ms.stats:
                list_t.append((i.category, i.total_distance_float))
            chart = BarsChart(
                results=dict(list_t),
                colors=list(
                    map(lambda a: tau.get_color(a.category), ms.stats)
                ),
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
            for a in ms.stats:
                box.pack_start(SummarySport(a), False, False, 0)
        else:
            label = Gtk.Label(_("There are not stats for this date"))
            label.set_yalign(0.0)
            label.get_style_context().add_class("pyot-h3")
            box.pack_start(label, False, False, 0)
            box.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_year_layout.ui")
class AggregatedStatsYear(Gtk.Box):
    """Gtk.Box with a combo box with year to load AnalyticTotalsYear."""

    __gtype_name__ = "AggregatedStatsYear"

    _combo_years: Gtk.ComboBox = Gtk.Template.Child()
    _year_list_store: Gtk.ListStore = Gtk.Template.Child()

    def __init__(self):
        """Load years in the combo box and load last AnalyticTotalsYear."""
        super().__init__()
        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)

        if years:
            self._year_totals = AnalyticTotalsYear(years[0])
            self.pack_start(self._year_totals, False, False, 0)
        else:
            label = Gtk.Label(_("There are not data"))
            label.get_style_context().add_class("pyot-h3")
            self.pack_start(label, False, False, 50)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            self.remove(self._year_totals)

            year = self._year_list_store[iter_item][1]

            self._year_totals = AnalyticTotalsYear(year)
            self.pack_start(self._year_totals, False, False, 0)


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
            lbl = Gtk.Label(label=_("There are not activities this year"))
            lbl.set_yalign(0.0)
            lbl.set_xalign(0.0)
            lbl.get_style_context().add_class("pyot-h3")
            self.pack_start(lbl, False, False, 50)
            self.show_all()
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
            _("Heart Rate\nAverage"),
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
            box_speed_pace_avg = self._build_info_box(aggregated.avg_speed)

            grid.attach(box_icon, 0, i + 1, 1, 1)
            grid.attach(box_activities, 1, i + 1, 1, 1)
            grid.attach(box_activities_per_month, 2, i + 1, 1, 1)
            grid.attach(box_distance, 3, i + 1, 1, 1)
            grid.attach(box_time, 4, i + 1, 1, 1)
            grid.attach(box_gain, 5, i + 1, 1, 1)
            grid.attach(box_hr_max, 6, i + 1, 1, 1)
            grid.attach(box_hr_avg, 7, i + 1, 1, 1)
            grid.attach(box_speed_pace_avg, 8, i + 1, 1, 1)
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
