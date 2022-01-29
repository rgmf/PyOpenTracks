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

from pyopentracks.app_preferences import AppPreferences


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/preferences_opentracks_layout.ui")
class PreferencesOpenTracksLayout(Gtk.Box):
    __gtype_name__ = "PreferencesOpenTracksLayout"

    _title: Gtk.Label = Gtk.Template.Child()
    _content_box: Gtk.Box = Gtk.Template.Child()
    _switch: Gtk.Switch = Gtk.Template.Child()
    _help_text: Gtk.Label = Gtk.Template.Child()

    def __init__(self, dialog):
        super().__init__()

        self._dialog = dialog

        self._title.set_text(_("Options for tracks recorded with OpenTracks"))
        self._title.get_style_context().add_class("pyot-h3")

        self._help_text.set_text(_(
            "Filter and correct elevation gain and loss for tracks "
            "recorded with OpenTracks"
        ))

        self._content_box.get_style_context().add_class("pyot-stats-bg-color")

        self._switch.connect("notify::active", self._on_gain_loss_activated)
        self._switch.set_active(
            self._dialog.get_pref(AppPreferences.OPENTRACKS_GAIN_LOSS_FILTER)
        )

    def _on_gain_loss_activated(self, switch, gparam):
        self._dialog.set_pref(
            AppPreferences.OPENTRACKS_GAIN_LOSS_FILTER,
            switch.get_active()
        )
