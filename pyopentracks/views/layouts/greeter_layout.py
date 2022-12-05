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

from pyopentracks.views.layouts.layout import Layout


class GreeterLayout(Gtk.Box, Layout):

    def __init__(self):
        super().__init__()
        Layout.__init__(self)

        self.set_spacing(10)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_homogeneous(False)

    def build(self):
        helptext = _(
            "You can:\n"
            "1.- Import a folder with activities.\n"
            "2.- Import an activity's file.\n"
            "3.- Select a folder to synchronize the activities files inside it."
        )
        labelh1 = Gtk.Label(label=_("Welcome to PyOpenTracks"))
        labelh1.get_style_context().add_class("pyot-h1")
        labelp = Gtk.Label(label=helptext)
        labelp.get_style_context().add_class("pyot-p-large")
        self.append(labelh1)
        self.append(labelp)
