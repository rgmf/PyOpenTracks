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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_summary_sport_layout.ui")
class SummarySport(Gtk.Box, Layout):
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
        self._aggregated = aggregated

    def build(self):
        self._icon.set_from_pixbuf(tau.get_icon_pixbuf(self._aggregated.category))
        self._sport_name.set_label(
            self._aggregated.category if self._aggregated.category else _("Unknown")
        )
        self._total_activities.set_label(str(self._aggregated.total_activities))
        self._total_time.set_label(self._aggregated.total_time)
        self._total_moving_time.set_label(self._aggregated.total_moving_time)
        self._total_distance.set_label(self._aggregated.total_distance)
        self._total_gain.set_label(self._aggregated.total_elevation_gain)
        self._avg_time.set_label(self._aggregated.avg_time)
        self._avg_moving_time.set_label(self._aggregated.avg_moving_time)
        self._avg_distance.set_label(self._aggregated.avg_distance)
        self._avg_gain.set_label(self._aggregated.avg_elevation_gain)
        self._avg_speed.set_label(self._aggregated.avg_speed)
        self._avg_speed_label.set_label(self._aggregated.speed_label)
        self._avg_heart_rate.set_label(self._aggregated.avg_heart_rate)
        self._max_time.set_label(self._aggregated.max_time)
        self._max_moving_time.set_label(self._aggregated.max_moving_time)
        self._max_distance.set_label(self._aggregated.max_distance)
        self._max_gain.set_label(self._aggregated.max_elevation_gain)
        self._max_speed.set_label(self._aggregated.max_speed)
        self._max_speed_label.set_label(self._aggregated.speed_label)
        self._max_heart_rate.set_label(self._aggregated.max_heart_rate)
        self.show_all()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/analytic_summary_time_sport_layout.ui")
class SummaryTimeSport(Gtk.Box, Layout):
    """Gtk.Box with total, averages and maximum stats for a time's sport.

    From AggregatedStats model builds a layout with totals, averages and
    maximums stats.
    """

    __gtype_name__ = "SummaryTimeSport"

    _icon: Gtk.Image = Gtk.Template.Child()
    _sport_name: Gtk.Label = Gtk.Template.Child()

    _total_activities: Gtk.Label = Gtk.Template.Child()
    _total_time: Gtk.Label = Gtk.Template.Child()
    _total_moving_time: Gtk.Label = Gtk.Template.Child()

    _avg_time: Gtk.Label = Gtk.Template.Child()
    _avg_moving_time: Gtk.Label = Gtk.Template.Child()
    _avg_heart_rate: Gtk.Label = Gtk.Template.Child()

    _max_time: Gtk.Label = Gtk.Template.Child()
    _max_moving_time: Gtk.Label = Gtk.Template.Child()
    _max_heart_rate: Gtk.Label = Gtk.Template.Child()

    def __init__(self, aggregated):
        """Fill Gtk.Box with the AggregatedStats model (aggregated)."""
        super().__init__()
        self._aggregated = aggregated

    def build(self):
        self._icon.set_from_pixbuf(tau.get_icon_pixbuf(self._aggregated.category))
        self._sport_name.set_label(
            self._aggregated.category if self._aggregated.category else _("Unknown")
        )
        self._total_activities.set_label(str(self._aggregated.total_activities))
        self._total_time.set_label(self._aggregated.total_time)
        self._total_moving_time.set_label(self._aggregated.total_moving_time)
        self._avg_time.set_label(self._aggregated.avg_time)
        self._avg_moving_time.set_label(self._aggregated.avg_moving_time)
        self._avg_heart_rate.set_label(self._aggregated.avg_heart_rate)
        self._max_time.set_label(self._aggregated.max_time)
        self._max_moving_time.set_label(self._aggregated.max_moving_time)
        self._max_heart_rate.set_label(self._aggregated.max_heart_rate)
        self.show_all()
