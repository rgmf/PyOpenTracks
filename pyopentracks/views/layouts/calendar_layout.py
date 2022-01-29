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
import calendar

from gi.repository import Gtk

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.views.graphs import StackedBarsChart
from pyopentracks.tasks.calendar_stats import CalendarStats
from pyopentracks.views.layouts.process_view import ProcessView


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/calendar_layout.ui")
class CalendarLayout(Gtk.Box):
    __gtype_name__ = "CalendarLayout"

    _label_month: Gtk.Label = Gtk.Template.Child()
    _grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self, month: int, year: int):
        """
        Arguments:
        month -- month's number from 1 (January) to 12 (December).
        year -- year's number.
        """
        super().__init__()

        self._label_month.get_style_context().add_class("pyot-h3")
        self._label_month.set_label(calendar.month_name[month])

        self._add_header_to_grid()

        ProcessView(self._calendar_ready, CalendarStats.run, (month, year)).start()

    def _calendar_ready(self, calendar_stats):
        for day in calendar_stats.days:
            self._add_item_to_grid(day.day, day.tracks, day.column, day.row)
        for week in calendar_stats.weeks:
            self._add_aggregated_stats_to_grid(week.aggregated_list, week.week, week.max_value)

        self.show_all()

    def _add_header_to_grid(self):
        for i in range(0, 7):
            label = Gtk.Label(calendar.day_abbr[i])
            label.get_style_context().add_class("pyot-h3")
            self._grid.attach(label, i, 0, 1, 1)

    def _add_item_to_grid(self, day, tracks, left, top):
        vbox = Gtk.VBox()
        hbox = Gtk.HBox()

        vbox.set_homogeneous(True)
        hbox.set_homogeneous(True)

        for track in tracks:
            icon = Gtk.Image()
            icon.set_from_pixbuf(tau.get_icon_pixbuf(track.activity_type, 36, 36))
            hbox.pack_start(icon, True, True, 0)

        vbox.pack_start(Gtk.Label(str(day)), True, True, 0)
        vbox.pack_start(hbox, True, True, 0)
        vbox.get_style_context().add_class("pyot-stats-bg-color")

        self._grid.attach(vbox, left, top, 1, 1)

    def _add_aggregated_stats_to_grid(self, aggregated_stats_list, top, max_moving_time):
        if aggregated_stats_list:
            results = {"": list(map(lambda o: o.total_moving_time_ms if o else 0, aggregated_stats_list))}
            colors = list(map(lambda o: tau.get_color(o.category) if o else None, aggregated_stats_list))
        else:
            results = {"": [0]}
            colors = None

        graph = StackedBarsChart(
            results,
            colors=colors,
            max_width=max_moving_time,
            cb_annotate=lambda value: tu.ms_to_str(value, True)
        )
        self._grid.attach(graph.get_canvas(), 7, top, 4, 1)
        graph.draw_and_show()
