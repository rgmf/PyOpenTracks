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

from pyopentracks.views.layouts.track_stats_layout import TrackStatsLayout
from pyopentracks.views.layouts.greeter_layout import GreeterLayout
from pyopentracks.views.layouts.tracks_layout import TracksLayout
from pyopentracks.views.layouts.info_layout import InfoLayout
from pyopentracks.utils.utils import TrackPointUtils
from pyopentracks.views.dialogs import MessageDialogError
from pyopentracks.app_preferences import AppPreferences


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/window.ui")
class PyopentracksWindow(Gtk.ApplicationWindow):
    # TODO Describe what this app window offer and works
    # TODO Refactor all around the action buttons: edit, del, back buttons.
    __gtype_name__ = "PyopentracksWindow"

    _edit_btn: Gtk.Button = Gtk.Template.Child()
    _del_btn: Gtk.Button = Gtk.Template.Child()

    _primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()
    _preferences_menu_btn: Gtk.Button = Gtk.Template.Child()
    _analytic_menu_btn: Gtk.Button = Gtk.Template.Child()
    _back_btn: Gtk.Button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("size-allocate", self._on_window_state_event)
        self.connect("delete-event", self._on_destroy)
        self._width = None
        self._height = None
        self._is_maximized = None
        self._load_window_state()
        self._action_buttons_handlers = []
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
        self._analytic_menu_btn.connect(
            "clicked",
            lambda button: self._app.analytic_button_clicked(button)
        )
        self._primary_menu_btn.set_menu_model(menu)

    def show_infobar(self, itype, message, buttons):
        """Shows information about a task ont top widget.

        This method can be used to show a message to the user with
        the result of a background task.
        """
        top_widget = self._layout.get_top_widget()
        if not top_widget:
            return

        layout = InfoLayout(itype, message, buttons)
        top_widget.pack_start(layout, False, False, 0)
        layout.show_all()

    def connect_button_del(self, action_cb, *args):
        self._del_btn.show()
        handler_id = self._del_btn.connect("clicked", action_cb, *args)
        self._action_buttons_handlers.append({
            "widget": self._del_btn,
            "handler_id": handler_id
        })

    def connect_button_edit(self, action_cb, *args):
        self._edit_btn.show()
        handler_id = self._edit_btn.connect("clicked", action_cb, *args)
        self._action_buttons_handlers.append({
            "widget": self._edit_btn,
            "handler_id": handler_id
        })

    def disconnect_action_buttons(self):
        for dict_item in self._action_buttons_handlers:
            dict_item["widget"].disconnect(dict_item["handler_id"])
            dict_item["widget"].hide()
        self._action_buttons_handlers = []

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
            self.show_layout(layout)
            self._edit_btn.hide()
            self._del_btn.hide()
            self._back_btn.show()
            self._analytic_menu_btn.hide()
            self._preferences_menu_btn.hide()

    def load_tracks(self, tracks):
        """Load all tracks in the correspondig layout.

        Arguments:
        tracks -- a list of Track objects.
        """
        self._preferences_menu_btn.show()
        if tracks and len(tracks) > 0:
            self._analytic_menu_btn.show()
            self.show_layout(TracksLayout(self, tracks))
        else:
            self._analytic_menu_btn.hide()
            self.show_layout(GreeterLayout())

    def load_analytics(self, layout):
        self.show_layout(layout)
        self._back_btn.show()
        self._analytic_menu_btn.hide()
        self._preferences_menu_btn.hide()
        self._edit_btn.hide()
        self._del_btn.hide()

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

    def on_quit(self):
        self._save_state()

    def _load_window_state(self):
        prefs = AppPreferences()
        self._width = prefs.get_pref(AppPreferences.WIN_STATE_WIDTH)
        self._height = prefs.get_pref(AppPreferences.WIN_STATE_HEIGHT)
        self._is_maximized = prefs.get_pref(AppPreferences.WIN_STATE_IS_MAXIMIZED)
        if self._is_maximized or not (self._width and self._height):
            self.maximize()
        else:
            self.set_default_size(self._width, self._height)
            self.move(0, 0)

    def _save_state(self):
        prefs = AppPreferences()
        prefs.set_pref(AppPreferences.WIN_STATE_WIDTH, self._width)
        prefs.set_pref(AppPreferences.WIN_STATE_HEIGHT, self._height)
        prefs.set_pref(AppPreferences.WIN_STATE_IS_MAXIMIZED, self._is_maximized)

    def _on_window_state_event(self, widget, event):
        self._width, self._height = self.get_size()
        self._is_maximized = self.is_maximized()

    def _on_destroy(self, widget, event):
        self._save_state()
