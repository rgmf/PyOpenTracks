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
from itertools import chain
from typing import List

from gi.repository import Gtk

from pyopentracks.app_preferences import AppPreferences
from pyopentracks.models.section import Section
from pyopentracks.stats.track_activity_stats import IntervalStats, HrZonesStats
from pyopentracks.utils.utils import TypeActivityUtils, SensorUtils, TimeUtils, ZonesUtils
from pyopentracks.views.graphs import BarsChart
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.models.activity import Activity


def build_box(value):
    """Builds a box with a label with value and styling."""
    box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
    box.get_style_context().add_class("pyot-stats-bg-color")
    box.set_homogeneous(False)
    label = Gtk.Label.new(value)
    label.set_xalign(0.0)
    label.set_yalign(0.0)
    box.append(label)
    return box


class TrackActivityDataAnalyticLayout(Gtk.Box, Layout):

    def __init__(self, activity: Activity, preferences: AppPreferences):
        super().__init__()
        Layout.__init__(self)
        self.set_homogeneous(True)
        self.get_style_context().add_class("pyot-bg")
        self._activity: Activity = activity
        self._preferences = preferences

    def build(self):
        self.append(TrackActivityIntervalsLayout(self._activity.category, self._activity.sections))
        self.append(
            TrackActivityZonesLayout(
                self._activity.sections,
                self._preferences.get_pref(self._preferences.HEART_RATE_MAX),
                self._preferences.get_pref(self._preferences.HEART_RATE_ZONES)
            )
        )


class TrackActivityIntervalsLayout(Gtk.Box):

    def __init__(self, category, sections: List[Section]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._category = category
        self._track_points = list(chain(*[ section.track_points for section in sections ]))
        self._is_speed_activity = TypeActivityUtils.is_speed(self._category)

        self._intervals_grid = Gtk.Grid()
        self._intervals_grid.set_row_spacing(5)
        self._intervals_grid.set_column_spacing(5)
        self._intervals_grid.set_margin_start(10)
        self._intervals_grid.set_margin_end(10)
        self._intervals_grid.set_margin_top(10)
        self._intervals_grid.set_margin_bottom(10)

        self._title_label = Gtk.Label.new(_("Intervals"))
        self._title_label.get_style_context().add_class("pyot-h3")
        self._title_label.get_style_context().add_class("pyot-stats-bg-color")

        self._intervals_list_store = Gtk.ListStore.new([int, str])
        if not self._is_speed_activity:
            self._intervals_list_store.append([100, "100 m"])
            self._intervals_list_store.append([200, "200 m"])
            self._intervals_list_store.append([400, "400 m"])
            self._intervals_list_store.append([500, "500 m"])
            self._intervals_list_store.append([800, "800 m"])
        self._intervals_list_store.append([1000, "1 km"])
        self._intervals_list_store.append([2000, "2 km"])
        self._intervals_list_store.append([3000, "3 km"])
        self._intervals_list_store.append([4000, "4 km"])
        self._intervals_list_store.append([5000, "5 km"])
        self._intervals_list_store.append([10000, "10 km"])
        self._intervals_list_store.append([20000, "20 km"])
        self._intervals_list_store.append([50000, "50 km"])

        self._intervals_combo_box = Gtk.ComboBox.new_with_model(self._intervals_list_store)
        self._intervals_combo_box.set_halign(Gtk.Align.START)
        self._intervals_combo_box.set_hexpand(False)
        self._intervals_combo_box.set_margin_start(10)
        self._intervals_combo_box.set_margin_end(10)
        self._intervals_combo_box.set_margin_top(10)
        self._intervals_combo_box.set_margin_bottom(10)
        renderer_text = Gtk.CellRendererText()
        self._intervals_combo_box.pack_start(renderer_text, True)
        self._intervals_combo_box.add_attribute(renderer_text, "text", 1)
        self._intervals_combo_box.set_active(5)
        self._intervals_combo_box.connect("changed", self._build)

        self.append(self._title_label)
        self.append(self._intervals_combo_box)
        self.append(self._intervals_grid)

        self._build(self._intervals_combo_box)

    def _build(self, combobox):
        child = self._intervals_grid.get_first_child()
        while child is not None:
            self._intervals_grid.remove(child)
            child = self._intervals_grid.get_first_child()

        self._intervals_grid.attach(Gtk.Label.new(_("Distance")), 0, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Time")), 1, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Speed") if self._is_speed_activity else _("Pace")), 2, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Max.\nSpeed") if self._is_speed_activity else _("Max.\nPace")), 3, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Avg.\nHeart Rate")), 4, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Max.\nHeart Rate")), 5, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Gain")), 6, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label.new(_("Loss")), 7, 0, 1, 1)

        if not self._track_points:
            return

        iter_item = combobox.get_active_iter()
        if iter_item is None:
            return
        interval_m = self._intervals_list_store[iter_item][0]

        ProcessView(self._on_data_ready, self._data_loading, (interval_m,)).start()

    def _data_loading(self, interval_m):
        interval_stats = IntervalStats(self._category, interval_m)
        interval_stats.compute(self._track_points)
        return interval_stats.intervals

    def _on_data_ready(self, intervals):
        row = 1
        for interval in intervals:
            self._intervals_grid.attach(build_box(interval.distance_str), 0, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.time_str), 1, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.avg_speed_str), 2, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.max_speed_str), 3, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.avg_hr_str), 4, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.max_hr_str), 5, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.gain_elevation_str), 6, row, 1, 1)
            self._intervals_grid.attach(build_box(interval.loss_elevation_str), 7, row, 1, 1)
            row += 1


class TrackActivityZonesLayout(Gtk.Box):

    _title_label: Gtk.Label = Gtk.Template.Child()
    _hr_max_info_label: Gtk.Label = Gtk.Template.Child()
    _zones_grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self, sections: List[Section], hr_max: int, hr_zones: List[int]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._sections: List[Section] = sections
        self._hr_max = hr_max
        self._hr_percentage_zones: List[int] = hr_zones

        self._hr_bpm_zones: List[int] = list(
            map(
                lambda percentage:
                SensorUtils.round_to_int(percentage / 100 * self._hr_max), self._hr_percentage_zones[0:-1]
            )
        )

        self._title_label = Gtk.Label.new(_("Heart Rate Zones"))
        self._title_label.get_style_context().add_class("pyot-h3")
        self._title_label.get_style_context().add_class("pyot-stats-bg-color")
        self.append(self._title_label)

        if not (self._hr_max > 0 and list(filter(lambda i: i > 0, self._hr_percentage_zones))):
            self._hr_max_info_label = Gtk.Label.new(_("Set you heart rate zones in the preferences"))
            self.append(self._hr_max_info_label)
            return

        self._hr_max_info_label = Gtk.Label.new(_("Max. Heart Rate: ") + str(self._hr_max) + "ppm")
        self._hr_max_info_label.get_style_context().add_class("pyot-h3")
        self._hr_max_info_label.set_margin_top(20)
        self._hr_max_info_label.set_margin_bottom(20)
        self.append(self._hr_max_info_label)

        self._zones_grid = Gtk.Grid()
        self._zones_grid.set_halign(Gtk.Align.CENTER)
        self._zones_grid.set_row_spacing(5)
        self._zones_grid.set_column_spacing(5)

        self.append(self._zones_grid)

        ProcessView(self._on_data_ready, self._data_loading, None).start()

    def _data_loading(self):
        hr_zones_stats = HrZonesStats(self._hr_bpm_zones)
        stats = hr_zones_stats.compute(self._sections)
        total_time = hr_zones_stats.total_time

        return stats, total_time

    def _on_data_ready(self, data: tuple):
        stats, total_time = data
        if not list(filter(lambda i: len(i) > 1 and i[1] > 0, stats.items())):
            self._zones_grid.attach(Gtk.Label.new(_("There are not heart reate data")), 0, 1, 6, 1)
            return

        self._zones_grid.attach(Gtk.Label.new(_("Zone")), 0, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new(_("Description")), 1, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new(_("Bottom")), 2, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new(_("Up")), 3, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new(_("Time")), 4, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new(_("%")), 5, 0, 1, 1)

        bars_result = {}
        for idx, value in stats.items():
            hr_bottom = str(self._hr_bpm_zones[idx])
            hr_top = str(_("MAX")) if len(self._hr_bpm_zones) == idx + 1 else str(self._hr_bpm_zones[idx + 1])
            zone_code = "Z" + str(idx + 1)
            description_zone = ZonesUtils.description_hr_zone(zone_code)
            percentage = SensorUtils.round_to_int(value / total_time * 100)

            bars_result[zone_code] = percentage

            self._zones_grid.attach(build_box(zone_code), 0, idx + 1, 1, 1)
            self._zones_grid.attach(build_box(description_zone), 1, idx + 1, 1, 1)
            self._zones_grid.attach(build_box(hr_bottom), 2, idx + 1, 1, 1)
            self._zones_grid.attach(build_box(hr_top), 3, idx + 1, 1, 1)
            self._zones_grid.attach(build_box(TimeUtils.ms_to_str(value)), 4, idx + 1, 1, 1)
            self._zones_grid.attach(build_box(str(percentage)), 5, idx + 1, 1, 1)

        chart = BarsChart(
            results=bars_result,
            colors=list(
                map(lambda zc: ZonesUtils.get_color(zc), bars_result.keys())
            ),
            cb_annotate=lambda v: str(v) + "%"
        )
        chart_box = Gtk.Box()
        chart_box.set_margin_start(10)
        chart_box.set_margin_end(10)
        chart_box.get_style_context().add_class("pyot-stats-bg-color")
        chart_box.append(chart.get_canvas())
        self.append(chart_box)
        chart.draw_and_show()
