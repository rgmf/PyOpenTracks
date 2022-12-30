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

from pyopentracks.views.preferences.layout import PreferencesLayout


class PreferencesDialog(Gtk.Window):

    def __init__(self, parent, app, on_ok_button_clicked_cb):
        super().__init__()

        # General attributes
        self._preferences = {}
        self._app = app
        self._auto_import_folder = None

        # Window configuration
        self.set_title(_("PyOpenTracks: Preferences"))
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(800, 600)
        header_bar = Gtk.HeaderBar()
        self.set_titlebar(header_bar)

        # Header bar with buttons
        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", lambda b: self.destroy())
        ok_button = Gtk.Button.new_with_label(_("Ok"))
        ok_button.connect("clicked", on_ok_button_clicked_cb)
        header_bar.pack_start(cancel_button)
        header_bar.pack_end(ok_button)

        # Child of the window: a vertical box
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_child(self._box)

        # Load layout to the box
        preferences_layout = PreferencesLayout(self)
        preferences_layout.set_vexpand(True)
        self._box.append(preferences_layout)

    def get_pref(self, pref):
        if pref in self._preferences:
            return self._preferences[pref]
        return self._app.get_pref(pref)

    def get_default(self, pref):
        return self._app.get_pref_default(pref)

    def set_pref(self, pref, value):
        self._preferences[pref] = value

    def get_updated_preferences(self):
        return self._preferences

