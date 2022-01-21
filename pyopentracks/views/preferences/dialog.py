"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>

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
            flags=0
        )
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self._preferences = []
        self._app = app
        self._box = self.get_content_area()
        self._auto_import_folder = None

        self._setup_ui()

    def _setup_ui(self):
        self.set_default_size(800, 600)
        self._box.pack_start(PreferencesLayout(self), True, True, 0)

    def get_pref(self, pref):
        return self._app.get_pref(pref)

    def set_pref(self, pref, value):
        self._preferences.append({"pref": pref, "value": value})

    def get_updated_preferences(self):
        return self._preferences
