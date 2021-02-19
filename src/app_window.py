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

import os
from pathlib import Path

from gi.repository import Gtk, Gio

from pyopentracks.views.layout import TrackStatsLayout, GreeterLayout, TracksFolderLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/window.ui")
class PyopentracksWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "PyopentracksWindow"

    _primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("PyOpenTracks")
        self._app = kwargs["application"]
        self._layout = None
        self.show_layout(GreeterLayout())

    def show_layout(self, layout):
        if layout is self._layout:
            return

        if self._layout:
            self.remove(self._layout)

        self._layout = layout
        self.add(self._layout)
        self.show_all()

    def set_menu(self, menu: Gio.Menu):
        self._primary_menu_btn.set_menu_model(menu)

    def load_track_stats(self, track):
        """Load track stats layout with new track.

        Arguments:
        track -- Track object with all stats and information.
        """
        layout = TrackStatsLayout()
        layout.load_data(track)
        self.show_layout(layout)

    def load_tracks_folder(self, trackspath: str):
        """Load tracks folder layout.

        Arguments:
        trackspath -- path where tracks are.
        """
        if not trackspath or not os.path.isdir(trackspath):
            # TODO this message should be printed to LOG system when added.
            print(f"Error: path '{trackspath}' is not a valid one.")
            self.show_layout(GreeterLayout())
        else:
            self.show_layout(TracksFolderLayout(self._app, Path(trackspath)))

    def loading(self, total):
        """Handle a progress bar on the top of the loaded Layout.

        Show a progress bar or upload an existing one on top of the
        loaded Layout.

        total -- a float number between 0.0 and 1.0 indicating the
                 progress of the loading process.
        """
        top_widget = self._layout.get_top_widget()
        if not top_widget:
            return

        if total == 1.0:
            top_widget.foreach(
                lambda child: (
                    top_widget.remove(child)
                    if isinstance(child, Gtk.ProgressBar) else None
                )
            )
            return

        if (len(top_widget.get_children()) == 0 or not
                isinstance(top_widget.get_children()[0], Gtk.ProgressBar)):
            progress = Gtk.ProgressBar()
            top_widget.pack_start(progress, True, False, 0)
            progress.set_fraction(total)
            self.show_all()
        else:
            progress = top_widget.get_children()[0]
            progress.set_fraction(total)
