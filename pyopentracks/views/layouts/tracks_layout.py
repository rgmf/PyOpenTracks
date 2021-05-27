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
from pyopentracks.views.layouts.track_stats_layout import TrackStatsLayout
from pyopentracks.models.database import Database
from pyopentracks.views.dialogs import QuestionDialog, TrackEditDialog


class TrackRow(Gtk.ListBoxRow):

    def __init__(self, track):
        super().__init__()
        self._track = track
        self._build_ui()

    def _build_ui(self):
        label = Gtk.Label(label=self._track.name, xalign=0.0)
        label.get_style_context().add_class("pyot-list-tracks-label")
        self.add(label)

    def update_ui(self, track):
        """Update the row UI according to the new track data."""
        self._track = track
        for w in self.get_children():
            self.remove(w)
        self._build_ui()
        self.show_all()

    @property
    def track(self):
        return self._track


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/tracks_layout.ui")
class TracksLayout(Gtk.Box, Layout):
    __gtype_name__ = "TracksLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Paned = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    _list_widget: Gtk.ListBox = Gtk.Template.Child()
    _track_stats_widget: Gtk.ScrolledWindow = Gtk.Template.Child()

    def __init__(self, app_window, tracks):
        super().__init__()

        self._app_window = app_window

        self._db = Database()

        self._list_widget.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list_widget.connect('row-activated', self._on_row_activated)

        self._show_message(_("Select a track to view its stats..."))

        self._tracks = tracks
        self._load_data()

        self._select_row(0)

        self.show_all()

    def get_top_widget(self):
        return self._top_widget

    def on_remove(self, widget, row):
        """Callback to remove the row."""
        dialog = QuestionDialog(
            parent=self._app_window,
            title=_("Remove Track"),
            question=_(f"Do you really want to remove track {row.track.name}")
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.CANCEL:
            return

        try:
            idx = row.get_index()
            db = Database()
            db.delete(row.track)
            row.destroy()
            self._select_row(idx if len(self._list_widget.get_children()) > idx else idx - 1)
        except ValueError:
            # TODO use logger here.
            print(f"Error: deleting track {row.track.name}")

    def on_edit(self, widget, row):
        """Callback to edit the row."""
        dialog = TrackEditDialog(parent=self._app_window, track=row.track)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            track = dialog.get_track()
            try:
                db = Database()
                db.update(track)
                self._on_row_activated(self._list_widget, row)
                row.update_ui(track)
            except ValueError:
                # TODO use logger here.
                print(f"Error: updating track {row.track.name}")

    def _load_data(self):
        for track in self._tracks:
            row = TrackRow(track)
            self._list_widget.add(row)

    def _select_row(self, idx):
        row = self._list_widget.get_row_at_index(idx)
        if row:
            self._list_widget.select_row(row)
            self._on_row_activated(self._list_widget, row)
        else:
            self._show_message(_("Select a track to view its stats..."))
            self._app_window.disconnect_action_buttons()

    def _on_row_activated(self, listbox, row):
        if not row.track:
            self._show_message(_("There was an error and the track cannot be showed"))
            return
        layout = TrackStatsLayout()
        self._add_widget(layout)
        layout.load_data(row.track)
        self._app_window.disconnect_action_buttons()
        self._app_window.connect_button_del(self.on_remove, row)
        self._app_window.connect_button_edit(self.on_edit, row)

    def _show_message(self, msg):
        label = Gtk.Label(label=_("Select a track to view its stats..."))
        label.get_style_context().add_class("pyot-h1")
        self._add_widget(label)

    def _add_widget(self, widget):
        """Add the widget to _track_stats_widget.

        Arguments:
        widget -- the widget to add to ScrolledWindow _track_stats_widget.
        """
        if self._track_stats_widget and self._track_stats_widget.get_child():
            self._track_stats_widget.remove(
                self._track_stats_widget.get_child()
            )
        self._track_stats_widget.add(widget)
        self.show_all()
