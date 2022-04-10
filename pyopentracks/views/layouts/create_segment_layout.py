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

from gi.repository import Gtk, GObject

from pyopentracks.stats.track_stats import TrackStats
from pyopentracks.utils.utils import DistanceUtils, ElevationUtils


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/create_segment_layout.ui")
class CreateSegmentLayout(Gtk.Box, GObject.GObject):
    """A layout with a form and information about a segment to be created.

    It shows an input text to add a name to the segment and shows
    distance and elevation gain and loss information.

    This layout contains two buttons: cancel and create and emits the signal
    'track-stats-segment-ok' with name, distance, gain and loss data when user
    click on create button.
    """

    __gtype_name__ = "TrackStatsSegmentLayout"

    __gsignals__ = {
        "track-stats-segment-ok": (GObject.SIGNAL_RUN_FIRST, None, (str, float, float, float)),
        "track-stats-segment-cancel": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    _title_label: Gtk.Label = Gtk.Template.Child()
    _name_entry: Gtk.Entry = Gtk.Template.Child()

    _distance_img: Gtk.Image = Gtk.Template.Child()
    _distance_label: Gtk.Label = Gtk.Template.Child()

    _gain_img: Gtk.Image = Gtk.Template.Child()
    _gain_label: Gtk.Label = Gtk.Template.Child()

    _loss_img: Gtk.Image = Gtk.Template.Child()
    _loss_label: Gtk.Label = Gtk.Template.Child()

    _left_button: Gtk.Button = Gtk.Template.Child()
    _right_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._stats = None

        self._title_label.set_text(_("Create New Segment"))
        self._title_label.get_style_context().add_class("pyot-h3")

        self._name_entry.set_placeholder_text(_("Type Segment's Name"))
        self._name_entry.connect(
            "changed",
            lambda w: self._right_button.set_sensitive(bool(self._name_entry.get_text().strip()))
        )

        self._distance_img.set_from_resource("/es/rgmf/pyopentracks/icons/send-symbolic.svg")
        self._gain_img.set_from_resource("/es/rgmf/pyopentracks/icons/up-symbolic.svg")
        self._loss_img.set_from_resource("/es/rgmf/pyopentracks/icons/down-symbolic.svg")

        self._left_button.set_label(_("Cancel"))
        self._left_button.connect("clicked", self._left_button_clicked_cb)

        self._right_button.set_label(_("Create"))
        self._right_button.set_sensitive(False)
        self._right_button.connect("clicked", self._right_button_clicked_cb)

    def _left_button_clicked_cb(self, button):
        self.emit("track-stats-segment-cancel")
        self.destroy()

    def _right_button_clicked_cb(self, button):
        self.emit(
            "track-stats-segment-ok",
            self._name_entry.get_text().strip(),
            float(self._stats.total_distance),
            float(self._stats.gain_elevation) if self._stats.gain_elevation else 0,
            float(self._stats.loss_elevation) if self._stats.loss_elevation else 0
        )
        self.destroy()

    def set_stats(self, stats: TrackStats):
        self._stats = stats
        self._distance_label.set_text(DistanceUtils.m_to_str(stats.total_distance))
        self._gain_label.set_text(ElevationUtils.elevation_to_str(stats.gain_elevation))
        self._loss_label.set_text(ElevationUtils.elevation_to_str(stats.loss_elevation))