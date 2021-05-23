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

from pyopentracks.views.layouts.layout import Layout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/greeter_layout.ui")
class GreeterLayout(Gtk.Box, Layout):
    __gtype_name__ = "GreeterLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.show_all()

    def _setup_ui(self):
        helptext = _(
            "You can:\n"
            "1.- Import a folder with tracks.\n"
            "2.- Import a track's file.\n"
            "3.- Select a folder to synchronize the tracks files inside it."
        )
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)
        labelh1 = Gtk.Label(label=_("Welcome to PyOpenTracks"))
        labelh1.get_style_context().add_class("pyot-h1")
        labelp = Gtk.Label(label=helptext)
        labelp.get_style_context().add_class("pyot-p-large")
        vbox.pack_start(labelh1, False, False, 0)
        vbox.pack_start(labelp, False, False, 0)
        self._main_widget.pack_start(vbox, True, True, 0)

    def get_top_widget(self):
        return self._top_widget
