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


class InfoLayout(Gtk.InfoBar):

    def __init__(self, itype, message, buttons):
        """Creates the InfoBar.

        Arguments:
        itype -- Gtk.MessageType.
        message -- The message to show in the Gtk.InfoBar.
        buttons -- a list of buttons information. Each item is a
                   dictionary with following keys:
                   - text: button's text.
                   - cb: clicked's callback function.
        """
        super().__init__()
        self.set_message_type(itype)
        label = Gtk.Label(label=message, xalign=0.0)
        label.set_line_wrap(True)
        label.get_style_context().add_class("pyot-p-small")
        content_area = self.get_content_area()
        content_area.add(label)
        self._add_buttons(buttons)

    def _add_buttons(self, buttons):
        for b in buttons:
            btn = self.add_button(b["text"], Gtk.ResponseType.OK)
            btn.connect("clicked", b["cb"])
