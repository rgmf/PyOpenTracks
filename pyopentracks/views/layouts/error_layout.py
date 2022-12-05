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


class ErrorLayout(Gtk.Box, Layout):

    def __init__(self):
        super().__init__()
        Layout.__init__(self)

        self.set_spacing(10)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_homogeneous(False)

    def build(self):
        helptext = _("An error ocurred and Layout has not been able to be loaded")
        labelp = Gtk.Label(label=helptext)
        labelp.get_style_context().add_class("pyot-p-large")
        self.pack_start(labelp, False, False, 0)
        self.show_all()
