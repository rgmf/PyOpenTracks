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

from pyopentracks.stats.track_stats import IntervalStats
from pyopentracks.utils.utils import TypeActivityUtils


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_data_analytic_layout.ui")
class TrackDataAnalyticLayout(Gtk.Box):
    __gtype_name__ = "TrackDataAnalyticLayout"

    def __init__(self, track):
        super().__init__()
        self.get_style_context().add_class("pyot-bg")
        self._track = track

    def build(self):
        self.pack_start(TrackIntervalsLayout(self._track.category, self._track.track_points), True, True, 0)
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
            self._intervals_grid.attach(self._build_box(interval.distance_str), 0, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.time_str), 1, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.avg_speed_str), 2, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.max_speed_str), 3, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.avg_hr_str), 4, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.max_hr_str), 5, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.gain_elevation_str), 6, top, 1, 1)
            self._intervals_grid.attach(self._build_box(interval.loss_elevation_str), 7, top, 1, 1)
            top += 1

        self.show_all()

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        box.set_homogeneous(False)
        box.pack_start(Gtk.Label(label=value, xalign=0.0, yalign=0.0), True, True, 0)
        return box
