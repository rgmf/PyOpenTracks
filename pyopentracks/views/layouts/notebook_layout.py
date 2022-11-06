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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/notebook_layout.ui")
class NotebookLayout(Gtk.Notebook, Layout):
    """Generic Gtk.Notebook."""

    __gtype_name__ = "NotebookLayout"

    def __init__(self):
        """Init."""
        super().__init__()
        Layout.__init__(self)

    def build(self):
        self.show_all()

    def append(self, layout: Layout, label: str):
        """Add a new tab to the notebook.

        Every tab contains a scrolled window that contains the layout.

        Arguments:
        layout -- the widget that will be contained into the scrolled window.
        label -- the tab's label.
        """
        scrolled_win = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        viewport.add(layout)
        scrolled_win.add(viewport)

        label_widget = Gtk.Label(label)
        self.append_page(scrolled_win, label_widget)

    def get_layouts(self):
        for scrolled_win in self.get_children():
            yield scrolled_win.get_children()[0].get_children()[0]
