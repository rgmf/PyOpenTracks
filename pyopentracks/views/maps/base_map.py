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

from gi.repository import GtkClutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GtkChamplain


class BaseMap:
    def __init__(self):
        self._widget = GtkChamplain.Embed()
        self._view = self._widget.get_view()
        self._view.set_property('kinetic-mode', True)
        self._view.set_property('zoom-level', 5)
        self._view.set_reactive(True)

    def get_widget(self):
        return self._widget
