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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/window.ui")
class PyopentracksWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "PyopentracksWindow"

    _primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()
    _preferences_menu_btn: Gtk.Button = Gtk.Template.Child()
    _analytic_menu_btn: Gtk.Button = Gtk.Template.Child()
    _segments_menu_btn: Gtk.Button = Gtk.Template.Child()

    _back_btn: Gtk.Button = Gtk.Template.Child()
    _edit_btn: Gtk.Button = Gtk.Template.Child()
    _del_btn: Gtk.Button = Gtk.Template.Child()
    _detail_btn: Gtk.Button = Gtk.Template.Child()

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
        self.connect("size-allocate", self._on_window_state_event)
        self.connect("delete-event", self._on_destroy)
        self._width = None
        self._height = None
        self._is_maximized = None
        self._load_window_state()
        self.set_title("PyOpenTracks")
        self._app = kwargs["application"]
        self._container = AppWindowContainer()
        self.add(self._container)

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


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/app_window_container.ui")
class AppWindowContainer(Gtk.Box):
    __gtype_name__ = "AppWindowContainer"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _content_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    def set_layout(self, new_child):
        for c in self._content_widget.get_children():
            self._content_widget.remove(c)
        self._content_widget.pack_start(new_child, True, True, 0)

    def get_top_widget(self):
        return self._top_widget

    def get_layout(self):
        return self._content_widget.get_children()[0] if self._content_widget.get_children() else None
