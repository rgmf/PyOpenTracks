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


class PreferencesDialog(Gtk.Dialog):

    def __init__(self, parent, app):
        Gtk.Dialog.__init__(
            self,
            title=_("Preferences"),
            transient_for=parent,
            use_header_bar=True
        )
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("Ok"), Gtk.ResponseType.OK)
        self._preferences = {}
        self._app = app
        self._box = self.get_content_area()
        self._auto_import_folder = None

        self._setup_ui()

    def _setup_ui(self):
        self.set_default_size(800, 600)
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

