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

from pyopentracks.views.preferences.import_layout import PreferencesImportLayout
from pyopentracks.views.preferences.zones_layout import PreferencesZonesLayout


class PreferencesLayout(Gtk.Paned):

    def __init__(self, dialog):
        super().__init__()

        self._tree_view = Gtk.TreeView()

        self._layouts = [
            {"key": _("Training Zones"), "layout": PreferencesZonesLayout},
            {"key": _("Import"), "layout": PreferencesImportLayout}
        ]

        self._dialog = dialog
        self._treepath_selected = None

        self._list_store = Gtk.ListStore(int, str)
        for idx, layout in enumerate(self._layouts):
            self._list_store.append([idx, layout["key"]])

        renderer = Gtk.CellRendererText()
        renderer.set_padding(10, 10)

        self._tree_view.set_model(self._list_store)
        self._tree_view.append_column(Gtk.TreeViewColumn("", renderer, text=1))

        tree_selection = self._tree_view.get_selection()
        tree_selection.connect("changed", self._on_tree_selection_changed)

        self.set_start_child(self._tree_view)
        self.set_resize_start_child(False)
        self.set_shrink_start_child(False)

    def _on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        idx = model.get_value(treeiter, 0)
        self.set_end_child(self._layouts[idx]["layout"](self._dialog))
        self.set_resize_end_child(True)
        self.set_shrink_end_child(False)
