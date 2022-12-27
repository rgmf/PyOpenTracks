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

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.views.layouts.layout import Layout


class SummarySport(Gtk.Box, Layout):
    """Generic summary sport layout"""

    def __init__(self, aggregated):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self._aggregated = aggregated

        # Header box
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Image.new_from_pixbuf(tau.get_icon_pixbuf(self._aggregated.category))
        icon.set_pixel_size(32)
        lbl = Gtk.Label.new(self._aggregated.category if self._aggregated.category else _("Unknown"))
        lbl.get_style_context().add_class("pyot-h3")
        lbl.set_margin_start(20)
        header_box.append(icon)
        header_box.append(lbl)

        self.append(header_box)

        # Horizontal box for totals, averages, maximums or whatever stats
        self._h_stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._h_stats_box.set_margin_top(10)
        self._h_stats_box.set_homogeneous(True)
        self._h_stats_box.get_style_context().add_class("pyot-stats-bg-color")

        self.append(self._h_stats_box)

    def _header(self, text):
        lbl = Gtk.Label.new(text)
        lbl.get_style_context().add_class("pyot-h3")
        return lbl

    def _label(self, text):
        lbl = Gtk.Label.new(text)
        lbl.set_xalign(1.0)
        lbl.get_style_context().add_class("pyot-stats-header")
        return lbl

    def _value(self, text):
        lbl = Gtk.Label.new(text)
        lbl.set_xalign(0.0)
        lbl.get_style_context().add_class("pyot-stats-value")
        return lbl


class SummaryMovingSport(SummarySport):
    """Gtk.Box with total, averages and maximum stats for a moving sport.

    From AggregatedStats model builds a layout with totals, averages and
    maximums stats.
    """

    def __init__(self, aggregated):
        """Fill Gtk.Box with the AggregatedStats model (aggregated)."""
        super().__init__(aggregated)

    def build(self):
        # Totals
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Totals")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.attach(self._label(_("Activities")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_activities)), 1, 0, 1, 1)
        grid.attach(self._label(_("Total Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_moving_time)), 1, 2, 1, 1)
        grid.attach(self._label(_("Total Distance")), 0, 3, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_distance)), 1, 3, 1, 1)
        grid.attach(self._label(_("Elevation Gain")), 0, 4, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_elevation_gain)), 1, 4, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)

        # Averages
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Averages")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.attach(self._label(_("Time")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_time)), 1, 0, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_moving_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Distance")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_distance)), 1, 2, 1, 1)
        grid.attach(self._label(_("Elevation Gain")), 0, 3, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_elevation_gain)), 1, 3, 1, 1)
        grid.attach(self._label(self._aggregated.speed_label), 0, 4, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_speed)), 1, 4, 1, 1)
        grid.attach(self._label(_("Heart Rate")), 0, 5, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_heart_rate)), 1, 5, 1, 1)
        grid.attach(self._label(_("Cadence")), 0, 6, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_cadence)), 1, 6, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)

        # Maximums
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Maximums")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.attach(self._label(_("Time")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_time)), 1, 0, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_moving_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Distance")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_distance)), 1, 2, 1, 1)
        grid.attach(self._label(_("Elevation Gain")), 0, 3, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_elevation_gain)), 1, 3, 1, 1)
        grid.attach(self._label(self._aggregated.speed_label), 0, 4, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_speed)), 1, 4, 1, 1)
        grid.attach(self._label(_("Heart Rate")), 0, 5, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_heart_rate)), 1, 5, 1, 1)
        grid.attach(self._label(_("Cadence")), 0, 6, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_cadence)), 1, 6, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)


class SummaryTimeSport(SummarySport):
    """Gtk.Box with total, averages and maximum stats for a time's sport.

    From AggregatedStats model builds a layout with totals, averages and
    maximums stats.
    """

    def __init__(self, aggregated):
        """Fill Gtk.Box with the AggregatedStats model (aggregated)."""
        super().__init__(aggregated)

    def build(self):
        # Totals
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Totals")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.attach(self._label(_("Activities")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_activities)), 1, 0, 1, 1)
        grid.attach(self._label(_("Total Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.total_moving_time)), 1, 2, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)

        # Averages
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Averages")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        grid.attach(self._label(_("Time")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_time)), 1, 0, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_moving_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Heart Rate")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.avg_heart_rate)), 1, 2, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)

        # Maximums
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._header(_("Averages")))

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        grid.attach(self._label(_("Time")), 0, 0, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_time)), 1, 0, 1, 1)
        grid.attach(self._label(_("Moving Time")), 0, 1, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_moving_time)), 1, 1, 1, 1)
        grid.attach(self._label(_("Heart Rate")), 0, 2, 1, 1)
        grid.attach(self._value(str(self._aggregated.max_heart_rate)), 1, 2, 1, 1)
        box.append(grid)

        self._h_stats_box.append(box)

