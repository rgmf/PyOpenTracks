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
from typing import List

from gi.repository import Gio

from pyopentracks.utils import logging as pyot_logging


class AppPreferences:
    DB_VERSION = 0
    AUTO_IMPORT_FOLDER = 1
    WIN_STATE_WIDTH = 2
    WIN_STATE_HEIGHT = 3
    WIN_STATE_IS_MAXIMIZED = 4
    HEART_RATE_MAX = 5
    HEART_RATE_ZONES = 6
    LAST_FOLDER = 7

    _settings: Gio.Settings = None

    def __init__(self):
        self._settings = Gio.Settings.new("es.rgmf.pyopentracks")
        self._settings.connect("changed::activitiespath", self._on_settings_folder_changed)

    def get_pref(self, pref):
        if pref == AppPreferences.DB_VERSION:
            return self._settings.get_int("dbversion")
        elif pref == AppPreferences.AUTO_IMPORT_FOLDER:
            return self._settings.get_string("activitiespath")
        elif pref == AppPreferences.WIN_STATE_WIDTH:
            return self._settings.get_int("win-state-width")
        elif pref == AppPreferences.WIN_STATE_HEIGHT:
            return self._settings.get_int("win-state-height")
        elif pref == AppPreferences.WIN_STATE_IS_MAXIMIZED:
            return self._settings.get_boolean("win-state-is-maximized")
        elif pref == AppPreferences.HEART_RATE_MAX:
            return self._settings.get_int("heart-rate-max")
        elif pref == AppPreferences.HEART_RATE_ZONES:
            return self._get_zones()
        elif pref == AppPreferences.LAST_FOLDER:
            return self._settings.get_string("last-folder")

    def set_pref(self, pref, new_value):
        if pref == AppPreferences.DB_VERSION:
            self._settings.set_int("dbversion", new_value)
        elif pref == AppPreferences.AUTO_IMPORT_FOLDER:
            self._settings.set_string("activitiespath", new_value)
        elif pref == AppPreferences.WIN_STATE_WIDTH:
            self._settings.set_int("win-state-width", new_value)
        elif pref == AppPreferences.WIN_STATE_HEIGHT:
            self._settings.set_int("win-state-height", new_value)
        elif pref == AppPreferences.WIN_STATE_IS_MAXIMIZED:
            self._settings.set_boolean("win-state-is-maximized", new_value)
        elif pref == AppPreferences.HEART_RATE_MAX:
            self._settings.set_int("heart-rate-max", new_value)
        elif pref == AppPreferences.HEART_RATE_ZONES:
            self._set_zones(new_value)
        elif pref == AppPreferences.LAST_FOLDER:
            self._settings.set_string("last-folder", new_value)

    def get_default(self, pref):
        if pref == AppPreferences.DB_VERSION:
            self._settings.get_default_value("dbversion")
        elif pref == AppPreferences.AUTO_IMPORT_FOLDER:
            self._settings.get_default_value("activitiespath")
        elif pref == AppPreferences.WIN_STATE_WIDTH:
            self._settings.get_default_value("win-state-width")
        elif pref == AppPreferences.WIN_STATE_HEIGHT:
            self._settings.get_default_value("win-state-height")
        elif pref == AppPreferences.WIN_STATE_IS_MAXIMIZED:
            self._settings.get_default_value("win-state-is-maximized")
        elif pref == AppPreferences.HEART_RATE_MAX:
            self._settings.get_default_value("heart-rate-max")
        elif pref == AppPreferences.HEART_RATE_ZONES:
            self._settings.get_default_value("heart-rate-zones")
        elif pref == AppPreferences.LAST_FOLDER:
            self._settings.get_default_value("last-folder")

    def _on_settings_folder_changed(self, settings, key):
        #self._load_folder()
        # dialog = FolderChooserWindow(parent=self._window)
        # response = dialog.run()
        # if response == Gtk.ResponseType.OK:
        #     self._settings.set_string("activitiespath", dialog.get_filename())
        # dialog.destroy()
        pass

    def _get_zones(self):
        """Convert comma-separated zones to a list of integers with all percentages."""
        zones = self._settings.get_string("heart-rate-zones")
        try:
            zones_list = list(map(lambda z: int(z), zones.split(',')))
            if len(zones_list) != 6:
                raise Exception(f"There are too many zones: {len(zones_list)}. They have should be 6.")
        except Exception as error:
            pyot_logging.get_logger(__name__).exception(str(error))
            zones_list = list(map(lambda z: int(z), self._settings.get_default_value("heart-rate-zones")))
        return zones_list

    def _set_zones(self, new_value: List[int]):
        """Convert the list of numbers to comma-separated string of those numbers.

        It checks that new_value is an array of integer items, it has 6 items, and it's ordered.
        """
        if type(new_value) is not list or len(new_value) != 6 or sorted(new_value) != new_value:
            return
        self._settings.set_string("heart-rate-zones", ",".join(map(lambda n: str(n), new_value)))
