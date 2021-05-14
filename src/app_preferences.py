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

from gi.repository import Gio


class AppPreferences:
    DB_VERSION = 0
    AUTO_IMPORT_FOLDER = 1
    WIN_STATE_WIDTH = 2
    WIN_STATE_HEIGHT = 3
    WIN_STATE_IS_MAXIMIZED = 4

    _settings: Gio.Settings = None

    def __init__(self):
        self._settings = Gio.Settings.new("es.rgmf.pyopentracks")
        self._settings.connect(
            "changed::trackspath", self._on_settings_folder_changed
        )

    def get_pref(self, pref):
        if pref == AppPreferences.DB_VERSION:
            return self._settings.get_int("dbversion")
        elif pref == AppPreferences.AUTO_IMPORT_FOLDER:
            return self._settings.get_string("trackspath")
        elif pref == AppPreferences.WIN_STATE_WIDTH:
            return self._settings.get_int("win-state-width")
        elif pref == AppPreferences.WIN_STATE_HEIGHT:
            return self._settings.get_int("win-state-height")
        elif pref == AppPreferences.WIN_STATE_IS_MAXIMIZED:
            return self._settings.get_boolean("win-state-is-mamixmized")

    def set_pref(self, pref, new_value):
        if pref == AppPreferences.DB_VERSION:
            self._settings.set_int("dbversion", new_value)
        elif pref == AppPreferences.AUTO_IMPORT_FOLDER:
            self._settings.set_string("trackspath", new_value)
        elif pref == AppPreferences.WIN_STATE_WIDTH:
            self._settings.set_int("win-state-width", new_value)
        elif pref == AppPreferences.WIN_STATE_HEIGHT:
            self._settings.set_int("win-state-height", new_value)
        elif pref == AppPreferences.WIN_STATE_IS_MAXIMIZED:
            self._settings.set_boolean("win-state-is-mamixmized", new_value)

    def _on_settings_folder_changed(self, settings, key):
        #self._load_folder()
        # dialog = FolderChooserWindow(parent=self._window)
        # response = dialog.run()
        # if response == Gtk.ResponseType.OK:
        #     self._settings.set_string("trackspath", dialog.get_filename())
        # dialog.destroy()
        pass
