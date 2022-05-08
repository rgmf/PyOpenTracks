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

from pyopentracks.app_preferences import AppPreferences
from pyopentracks.stats.track_stats import IntervalStats, HrZonesStats
from pyopentracks.utils.utils import TypeActivityUtils, SensorUtils, TimeUtils, ZonesUtils
from pyopentracks.views.graphs import BarsChart


def build_box(value):
    """Builds a box with a label with value and styling."""
    box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
    box.get_style_context().add_class("pyot-stats-bg-color")
    box.set_homogeneous(False)
    box.pack_start(Gtk.Label(label=value, xalign=0.0, yalign=0.0), True, True, 0)
    return box


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_data_analytic_layout.ui")
class TrackDataAnalyticLayout(Gtk.Box):
    __gtype_name__ = "TrackDataAnalyticLayout"

    def __init__(self, track, preferences: AppPreferences):
        super().__init__()
        self.get_style_context().add_class("pyot-bg")
        self._track = track
        self._preferences = preferences

    def build(self):
        self.pack_start(TrackIntervalsLayout(self._track.category, self._track.track_points), True, True, 0)
        self.pack_start(
            TrackZonesLayout(
                self._track.track_points,
                self._preferences.get_pref(self._preferences.HEART_RATE_MAX),
                self._preferences.get_pref(self._preferences.HEART_RATE_ZONES)
            ),
            True, True, 0
        )
        self.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_intervals_layout.ui")
class TrackIntervalsLayout(Gtk.Box):
    __gtype_name__ = "TrackIntervalsLayout"

    _title_label: Gtk.Label = Gtk.Template.Child()
    _intervals_combo_box: Gtk.ComboBox = Gtk.Template.Child()
    _intervals_list_store: Gtk.ListStore = Gtk.Template.Child()
    _intervals_grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self, category, track_points):
        super().__init__()

        self._category = category
        self._track_points = track_points
        self._is_speed_track = TypeActivityUtils.is_speed(self._category)

        self._title_label.set_text(_("Intervals"))
        self._title_label.get_style_context().add_class("pyot-h3")
        self._title_label.get_style_context().add_class("pyot-stats-bg-color")

        if not self._is_speed_track:
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
        self._intervals_combo_box.set_active(5)
        self._intervals_combo_box.connect("changed", self._build)

        self._build(self._intervals_combo_box)

    def _build(self, combobox):
        for child in self._intervals_grid.get_children():
            self._intervals_grid.remove(child)

        self._intervals_grid.attach(Gtk.Label(_("Distance")), 0, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Time")), 1, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Speed") if self._is_speed_track else _("Pace")), 2, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Max.\nSpeed") if self._is_speed_track else _("Max.\nPace")), 3, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Avg.\nHeart Rate")), 4, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Max.\nHeart Rate")), 5, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Gain")), 6, 0, 1, 1)
        self._intervals_grid.attach(Gtk.Label(_("Loss")), 7, 0, 1, 1)

        if not self._track_points:
            return

        iter_item = combobox.get_active_iter()
        if iter_item is None:
            return
        interval_m = self._intervals_list_store[iter_item][0]

        top = 1
        interval_stats = IntervalStats(self._category, interval_m)
        interval_stats.compute(self._track_points)
        for interval in interval_stats.intervals:
            self._intervals_grid.attach(build_box(interval.distance_str), 0, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.time_str), 1, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.avg_speed_str), 2, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.max_speed_str), 3, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.avg_hr_str), 4, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.max_hr_str), 5, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.gain_elevation_str), 6, top, 1, 1)
            self._intervals_grid.attach(build_box(interval.loss_elevation_str), 7, top, 1, 1)
            top += 1

        self.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_zones_layout.ui")
class TrackZonesLayout(Gtk.Box):
    __gtype_name__ = "TrackZonesLayout"

    _title_label: Gtk.Label = Gtk.Template.Child()
    _hr_max_info_label: Gtk.Label = Gtk.Template.Child()
    _zones_grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self, track_points, hr_max: int, hr_zones: List[int]):
        super().__init__()

        self._hr_max = hr_max
        self._hr_percentage_zones: List[int] = hr_zones

        self._title_label.set_text(_("Heart Rate Zones"))
        self._title_label.get_style_context().add_class("pyot-h3")
        self._title_label.get_style_context().add_class("pyot-stats-bg-color")

        self._hr_max_info_label.set_text(_("Max. Heart Rate: ") + str(self._hr_max) + "ppm")
        self._hr_max_info_label.get_style_context().add_class("pyot-h3")

        self._zones_grid.attach(Gtk.Label(_("Zone")), 0, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label(_("Description")), 1, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label(_("Bottom")), 2, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label(_("Up")), 3, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label(_("Time")), 4, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label(_("%")), 5, 0, 1, 1)

        zones = list(
            map(lambda percentage: SensorUtils.round_to_int(percentage / 100 * hr_max), self._hr_percentage_zones[0:-1])
        )
        hr_zones_stats = HrZonesStats(zones)
        stats = hr_zones_stats.compute(track_points)
        total_time = hr_zones_stats.total_time
        bars_result = {}
        for idx, value in stats.items():
            hr_bottom = str(zones[idx])
            hr_top = str(_("MAX")) if len(zones) == idx + 1 else str(zones[idx + 1])
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
        chart_box.set_margin_left(10)
        chart_box.set_margin_right(10)
        chart_box.get_style_context().add_class("pyot-stats-bg-color")
        chart_box.pack_start(chart.get_canvas(), True, True, 10)
        self.pack_start(chart_box, False, False, 0)
        chart_box.show_all()
        chart.draw_and_show()
