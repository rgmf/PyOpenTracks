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
from pyopentracks.views.preferences.opentracks_layout import PreferencesOpenTracksLayout
from pyopentracks.views.preferences.zones_layout import PreferencesZonesLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/preferences_layout.ui")
class PreferencesLayout(Gtk.Paned):
    __gtype_name__ = "PreferencesLayout"

    _tree_view: Gtk.TreeView = Gtk.Template.Child()

    def __init__(self, dialog):
        super().__init__()

        self._layouts = [
            {"key": _("Training Zones"), "layout": PreferencesZonesLayout},
            {"key": _("Import"), "layout": PreferencesImportLayout},
            {"key": "OpenTracks", "layout": PreferencesOpenTracksLayout},
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

    def _on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        idx = model.get_value(treeiter, 0)
        if self.get_child2():
            self.remove(self.get_child2())
        self.pack2(self._layouts[idx]["layout"](self._dialog), True, True)
