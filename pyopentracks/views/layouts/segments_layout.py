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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segments_layout.ui")
class SegmentsLayout(Gtk.Notebook):
    __gtype_name__ = "SegmentsLayout"

    def __init__(self):
        super().__init__()

    def append(self, layout: Gtk.Widget, label: str):
        """Add a new tab to the notebook.

        Every tab contains a scrolled window that contains the layout.

        Arguments:
        layout -- the widget that will contained into the scrolled window.
        label  -- the tab's label.
        """
        scrolled_win = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        viewport.add(layout)
        scrolled_win.add(viewport)

        label_widget = Gtk.Label(label)
        self.append_page(scrolled_win, label_widget)
        self.show_all()
