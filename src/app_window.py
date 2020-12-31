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

from gi.repository import Gtk, Gio


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/window.ui")
class PyopentracksWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "PyopentracksWindow"

    label: Gtk.Label = Gtk.Template.Child()
    primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_menu(self, menu: Gio.Menu):
        self.primary_menu_btn.set_menu_model(menu)
