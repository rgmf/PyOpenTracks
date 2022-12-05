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


class NotebookLayout(Gtk.Notebook, Layout):
    """Generic Gtk.Notebook."""

    def __init__(self):
        """Init."""
        super().__init__()
        Layout.__init__(self)

    def build(self):
        #self.show_all()
        pass

    def append(self, layout: Layout, label: str):
        """Add a new tab to the notebook.

        Every tab contains a scrolled window that contains the layout.

        Arguments:
        layout -- the widget that will be contained into the scrolled window.
        label -- the tab's label.
        """
        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.set_child(layout)

        label_widget = Gtk.Label.new(label)
        self.append_page(scrolled_win, label_widget)

    def get_layouts(self):
        list_model = self.get_pages()
        for i in range(list_model.get_n_items()):
            notebook_page = list_model.get_item(i)
            scrolled_win = notebook_page.get_child()
            child = scrolled_win.get_first_child() if scrolled_win is not None else None
            if isinstance(child, Gtk.Viewport):
                yield child.get_first_child()
            else:
                yield child

