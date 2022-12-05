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
from pyopentracks.models.stats import Stats


class CreateSegmentLayout(Gtk.Box, GObject.GObject):
    """A layout with a form and information about a segment to be created.

    It shows an input text to add a name to the segment and shows
    distance and elevation gain and loss information.

    This layout contains two buttons: cancel and create and emits the signal
    'track-stats-segment-ok' with name, distance, gain and loss data when user
    click on create button.
    """

    __gsignals__ = {
        "track-activity-stats-segment-ok": (GObject.SIGNAL_RUN_FIRST, None, (str, float, float, float)),
        "track-activity-stats-segment-cancel": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self._stats = None

        self._title_label = Gtk.Label.new(_("Create New Segment"))
        self._title_label.get_style_context().add_class("pyot-h3")

        self._name_entry = Gtk.Entry()
        self._name_entry.set_placeholder_text(_("Type Segment's Name"))
        self._name_entry.connect(
            "changed",
            lambda w: self._right_button.set_sensitive(bool(self._name_entry.get_text().strip()))
        )

        box_with_stats = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        box_distance = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self._distance_img = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/send-symbolic.svg")
        self._distance_label = Gtk.Label()
        box_distance.append(self._distance_img)
        box_distance.append(self._distance_label)

        box_gain = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self._gain_img = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/up-symbolic.svg")
        self._gain_label = Gtk.Label()
        box_gain.append(self._gain_img)
        box_gain.append(self._gain_label)

        box_loss = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self._loss_img = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/down-symbolic.svg")
        self._loss_label = Gtk.Label()
        box_loss.append(self._loss_img)
        box_loss.append(self._loss_label)

        box_with_stats.append(box_distance)
        box_with_stats.append(box_gain)
        box_with_stats.append(box_loss)

        box_with_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._left_button = Gtk.Button.new_with_label(_("Cancel"))
        self._left_button.connect("clicked", self._left_button_clicked_cb)
        self._right_button = Gtk.Button.new_with_label(_("Create"))
        self._right_button.set_sensitive(False)
        self._right_button.connect("clicked", self._right_button_clicked_cb)
        box_with_buttons.append(self._left_button)
        box_with_buttons.append(self._right_button)

        self.append(self._title_label)
        self.append(self._name_entry)
        self.append(box_with_stats)
        self.append(box_with_buttons)

    def _left_button_clicked_cb(self, button):
        self.emit("track-activity-stats-segment-cancel")
        self._name_entry.set_text("")

    def _right_button_clicked_cb(self, button):
        self.emit(
            "track-activity-stats-segment-ok",
            self._name_entry.get_text().strip(),
            float(self._stats.total_distance_m),
            float(self._stats.gain_elevation_m) if self._stats.gain_elevation_m else 0,
            float(self._stats.loss_elevation_m) if self._stats.loss_elevation_m else 0
        )
        self._name_entry.set_text("")

    def set_stats(self, stats: Stats):
        self._stats = stats
        self._distance_label.set_text(stats.total_distance)
        self._gain_label.set_text(stats.gain_elevation)
        self._loss_label.set_text(stats.loss_elevation)

