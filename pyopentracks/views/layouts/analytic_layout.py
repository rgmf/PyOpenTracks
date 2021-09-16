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

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.utils.utils import DateUtils as du
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.graphs import AggregatedStatsChart
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


@Gtk.Template(
    resource_path="/es/rgmf/pyopentracks/ui/analytic_summary_sport_layout.ui"
)
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


@Gtk.Template(
    resource_path="/es/rgmf/pyopentracks/ui/analytic_year_layout.ui"
)
class AggregatedStatsYear(Gtk.Box):
    __gtype_name__ = "AggregatedStatsYear"

    _combo_years: Gtk.ComboBox = Gtk.Template.Child()
    _year_list_store: Gtk.ListStore = Gtk.Template.Child()
    _box: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui(DatabaseHelper.get_years())

    def _setup_ui(self, years):
        for y in years:
            self._year_list_store.append([y, y])
        self._combo_years.set_active(0)
        self._combo_years.connect("changed", self._on_year_changed)
        self._year_stack = AnalyticYearStack(years[0])
        self._box.pack_start(self._year_stack, False, False, 0)

    def _on_year_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            for child in self._box.get_children():
                self._box.remove(child)
            year = self._year_list_store[iter_item][1]
            self._year_stack = AnalyticYearStack(year)
            self._box.pack_start(self._year_stack, False, False, 0)


@Gtk.Template(
    resource_path="/es/rgmf/pyopentracks/ui/analytic_year_stack_layout.ui"
)
class AnalyticYearStack(Gtk.Box):
    __gtype_name__ = "AnalyticYearStack"

    _stack_switcher: Gtk.StackSwitcher = Gtk.Template.Child()
    _stack: Gtk.Stack = Gtk.Template.Child()

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
            data_list[str(year) + str(month)] = {
                "aggregated_list": DatabaseHelper.get_aggregated_stats(
                    date_from=date_from, date_to=date_to
                ),
                "month": month,
                "month_name": month_name
            }
            month = month + 1
        return data_list

    def _on_stack_data_ready(self, data_list):
        self._data_list = data_list
        for idx in self._data_list:
            data = self._data_list[idx]
            month = data["month"]
            month_name = data["month_name"]
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
        aggregated_list = data["aggregated_list"]
        if aggregated_list:
            chart = AggregatedStatsChart(aggregated_list)
            box.pack_start(chart.get_canvas(), False, False, 0)
            chart.draw_and_show()
            for a in aggregated_list:
                box.pack_start(SummarySport(a), False, False, 0)
        else:
            label = Gtk.Label(_("There are not stats for this date"))
            label.set_yalign(0.0)
            label.get_style_context().add_class("pyot-h1")
            box.pack_start(label, False, False, 0)
