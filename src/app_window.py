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

from gi.repository import Gtk, Gio

from pyopentracks.views.layout import (
    TrackStatsLayout, GreeterLayout, TracksLayout, InfoLayout
)
from pyopentracks.utils.utils import TrackPointUtils
from pyopentracks.views.dialogs import MessageDialogError


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/window.ui")
class PyopentracksWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "PyopentracksWindow"

    _primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()
    _preferences_menu_btn: Gtk.Button = Gtk.Template.Child()
    _back_btn: Gtk.Button = Gtk.Template.Child()

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

    def set_menu(self, menu: Gio.Menu):
        self._back_btn.connect(
            "clicked",
            lambda button: self._app.back_button_clicked(button)
        )
        self._preferences_menu_btn.connect(
            "clicked",
            lambda button: self._app.preferences_button_clicked(button)
        )
        self._primary_menu_btn.set_menu_model(menu)

    def show_background_task_message(self, title, message, buttons):
        """Shows information about a task ont top widget.

        This method can be used to show a message to the user with
        the result of a background task.
        """
        top_widget = self._layout.get_top_widget()
        if not top_widget:
            return

        layout = InfoLayout(title, message)
        for b in buttons:
            layout.append_button(b)
        top_widget.pack_start(layout, True, False, 10)
        layout.show_all()

    def load_track_stats(self, result: dict):
        """Load track stats layout with new track.

        Arguments:
        result -- dictionary with the following keys:
                  - file: path's file.
                  - track: Track object or None if any error.
                  - error: message's error or None.
        """
        track = result["track"]
        if not track:
            MessageDialogError(
                transient_for=self,
                text=(
                    _(f"Error opening the file {result['file']}") +
                    ": \n" + result["message"]
                ),
                title=_("Error opening track file")
            ).show()
        else:
            layout = TrackStatsLayout()
            layout.load_data(track)
            layout.load_map(TrackPointUtils.to_locations(track.track_points))
            self.show_layout(layout)
            self._back_btn.show()

    def load_tracks(self, tracks):
        """Load all tracks in the correspondig layout.

        Arguments:
        tracks -- a list of Track objects.
        """
        if tracks and len(tracks) > 0:
            self.show_layout(TracksLayout(self._app, tracks))
        else:
            self.show_layout(GreeterLayout())

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
            top_widget.show_all()
        else:
            progress = top_widget.get_children()[0]
            progress.set_fraction(total)

    def clean_top_widget(self):
        widget = self._layout.get_top_widget()
        widget.foreach(lambda child: widget.remove(child))
