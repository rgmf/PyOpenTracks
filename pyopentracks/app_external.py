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

from gi.repository import Gtk, GObject

from pyopentracks.app_interfaces import Action


class AppExternal(GObject.GObject):

    __gsignals__ = {
        "actions-changed": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        GObject.GObject.__init__(self)

    def get_layout(self):
        """Return the main layout of the external app"""
        raise "get_layout must be implemented"

    def get_actions(self) -> List[Action]:
        """Never return None, if any then return empty list []"""
        raise "get_actions must be implemented"

    def get_kwargs(self) -> dict:
        """Return the dictionary of arguments needed to rebuild the external app"""
        raise "get_kwargs must be implemented"

    def get_window(self) -> Gtk.Window:
        raise "get_window must be implemented"

