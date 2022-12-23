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
from enum import Enum

from gi.repository import Gtk, Gio

from pyopentracks.views.layouts.info_layout import InfoLayout
from pyopentracks.app_preferences import AppPreferences


class PyopentracksWindow(Gtk.ApplicationWindow):

    class MenuButton(Enum):
        MAIN = 0
        PREFERENCES = 1
        ANALYTIC = 2
        SEGMENTS = 3

    class ActionButton(Enum):
        BACK = 0
        DELETE = 1
        EDIT = 2
        DETAIL = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._width = None
        self._height = None
        self._is_maximized = None
        self._load_window_state()
        self._app = kwargs["application"]
        self._container = AppWindowContainer()

        self.connect("close-request", self._on_window_close_request)

        self.set_title("PyOpenTracks")
        self.set_child(self._container)

        self._primary_menu_btn = Gtk.MenuButton()
        self._primary_menu_btn.set_icon_name("open-menu-pyot")
        self._preferences_menu_btn = Gtk.Button()
        self._preferences_menu_btn.set_icon_name("settings-symbolic")
        self._analytic_menu_btn = Gtk.Button()
        self._analytic_menu_btn.set_icon_name("stats-symbolic")
        self._segments_menu_btn = Gtk.Button()
        self._segments_menu_btn.set_icon_name("map-symbolic")
        self._back_btn = Gtk.Button()
        self._back_btn.set_icon_name("left-symbolic")
        self._del_btn = Gtk.Button()
        self._del_btn.set_icon_name("trash-symbolic")
        self._edit_btn = Gtk.Button()
        self._edit_btn.set_icon_name("edit-symbolic")
        self._detail_btn = Gtk.Button()
        self._detail_btn.set_icon_name("paper-symbolic")

        self._header_bar = Gtk.HeaderBar()
        self.set_titlebar(self._header_bar)
        self._header_bar.pack_end(self._primary_menu_btn)
        self._header_bar.pack_end(self._preferences_menu_btn)
        self._header_bar.pack_end(self._analytic_menu_btn)
        self._header_bar.pack_end(self._segments_menu_btn)
        self._header_bar.pack_start(self._back_btn)
        self._header_bar.pack_start(self._del_btn)
        self._header_bar.pack_start(self._edit_btn)
        self._header_bar.pack_start(self._detail_btn)

        self._menu_buttons = {
            PyopentracksWindow.MenuButton.MAIN: self._primary_menu_btn,
            PyopentracksWindow.MenuButton.PREFERENCES: self._preferences_menu_btn,
            PyopentracksWindow.MenuButton.ANALYTIC: self._analytic_menu_btn,
            PyopentracksWindow.MenuButton.SEGMENTS: self._segments_menu_btn,
        }
        self._action_buttons = {
            PyopentracksWindow.ActionButton.BACK: self._back_btn,
            PyopentracksWindow.ActionButton.DELETE: self._del_btn,
            PyopentracksWindow.ActionButton.EDIT: self._edit_btn,
            PyopentracksWindow.ActionButton.DETAIL: self._detail_btn,
        }
        self._action_buttons_handlers = []

        for _, value in self._menu_buttons.items():
            value.hide()

        for _, value in self._action_buttons.items():
            value.hide()

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
        self._segments_menu_btn.connect(
            "clicked",
            lambda button: self._app.segments_button_clicked(button)
        )
        self._primary_menu_btn.set_menu_model(menu)

    def show_infobar(self, itype, message, buttons):
        """Shows information about a task ont top widget.

        This method can be used to show a message to the user with
        the result of a background task.
        """
        top_widget = self._container.get_top_widget()
        if not top_widget:
            return

        layout = InfoLayout(itype, message, buttons)
        top_widget.pack_start(layout, False, False, 0)
        top_widget.show_all()

    def set_visibility_menu_buttons(self, visible: bool):
        self._primary_menu_btn.set_visible(visible)
        self._preferences_menu_btn.set_visible(visible)
        self._analytic_menu_btn.set_visible(visible)
        self._segments_menu_btn.set_visible(visible)

    def connect_action_button(self, button_id: ActionButton, callback, args):
        if not button_id or button_id not in self._action_buttons:
            return
        button = self._action_buttons[button_id]
        button.show()
        handler_id = button.connect("clicked", callback, args)
        self._action_buttons_handlers.append({
            "widget": button,
            "handler_id": handler_id
        })

    def disconnect_action_buttons(self):
        for dict_item in self._action_buttons_handlers:
            dict_item["widget"].disconnect(dict_item["handler_id"])
            dict_item["widget"].hide()
        self._action_buttons_handlers = []

    def load_app(self, app):
        if app.get_layout() is self._container.get_layout():
            return
        self._container.set_layout(app.get_layout())

    def loading(self, total):
        """Handle a progress bar on the top of the loaded Layout.

        Show a progress bar or upload an existing one on top of the
        loaded Layout.

        total -- a float number between 0.0 and 1.0 indicating the
                 progress of the loading process.
        """
        top_widget = self._container.get_top_widget()
        if not top_widget:
            return

        if total == 1.0:
            child = top_widget.get_first_child()
            if child is not None and isinstance(child, Gtk.ProgressBar):
                top_widget.remove(child)
            return

        if top_widget.get_first_child() is None or not isinstance(top_widget.get_first_child(), Gtk.ProgressBar):
            progress = Gtk.ProgressBar()
            progress.set_hexpand(True)
            top_widget.append(progress)
            progress.set_fraction(total)
        else:
            progress = top_widget.get_first_child()
            progress.set_fraction(total)

    def clean_top_widget(self):
        widget = self._container.get_top_widget()
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

    def _save_state(self):
        prefs = AppPreferences()
        prefs.set_pref(AppPreferences.WIN_STATE_WIDTH, self._width)
        prefs.set_pref(AppPreferences.WIN_STATE_HEIGHT, self._height)
        prefs.set_pref(AppPreferences.WIN_STATE_IS_MAXIMIZED, self._is_maximized)

    def _on_window_close_request(self, window):
        self._width, self._height = self.get_default_size()
        self._is_maximized = self.is_maximized()
        self._save_state()

    def _on_destroy(self, widget, event):
        self._save_state()


class AppWindowContainer(Gtk.Box):

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._top_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._content_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.append(self._top_widget)
        self.append(self._content_widget)

    def set_layout(self, new_child):
        child = self._content_widget.get_first_child()
        while child is not None:
            self._content_widget.remove(child)
            child = self._content_widget.get_first_child()
        self._content_widget.append(new_child)

    def get_top_widget(self):
        return self._top_widget

    def get_layout(self):
        return self._content_widget.get_first_child() if self._content_widget.get_first_child() else None
