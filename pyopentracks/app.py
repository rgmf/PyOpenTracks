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
from dataclasses import dataclass, field
from typing import List

from gi.repository import Gtk, Gio, Gdk, GLib

from pyopentracks.app_interfaces import Action
from pyopentracks.app_activity_list import AppActivityList
from pyopentracks.app_activity_info import AppActivityInfo
from pyopentracks.utils import logging as pyot_logging
from pyopentracks.app_preferences import AppPreferences
from pyopentracks.app_window import PyopentracksWindow
from pyopentracks.views.file_chooser import (
    ImportFileChooserDialog, ImportFolderChooserWindow, FolderChooserWindow, FileChooserWindow
)
from pyopentracks.models.migrations import Migration
from pyopentracks.models.database import Database
from pyopentracks.views.preferences.dialog import PreferencesDialog
from pyopentracks.views.dialogs import (
    ImportResultDialog,
    ExportResultDialog,
    MessageDialogError
)
from pyopentracks.app_analytic import AppAnalytic
from pyopentracks.app_segments import AppSegments
from pyopentracks.io.parser.factory import ParserFactory
from pyopentracks.io.proxy.proxy import RecordProxy


class Application(Gtk.Application):

    @dataclass
    class AppLoaded:
        class_var: any
        kwargs: dict = field(default_factory=dict)
        actions: List[Action] = None
        show_menu_buttons: bool = False

        def instance(self, app):
            return self.class_var(app, self.args)

    def __init__(self, app_id):
        super().__init__(
            application_id=app_id,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.add_main_option(
            "loglevel",
            ord("l"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.INT,
            "Log level: Critical (5), Error (4), Warning (3), Info (2), Debug (1)",
            None,
        )
        self._menu: Gio.Menu = Gio.Menu()
        self._window: PyopentracksWindow = None
        self._preferences: AppPreferences = None
        self._apps_queue: List[Application.AppLoaded] = []

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PyopentracksWindow(application=self)
        self._window = win

        provider = Gtk.CssProvider()
        provider.load_from_resource("/es/rgmf/pyopentracks/ui/gtk_style.css")
        style_context = self._window.get_style_context()
        if style_context is not None:
            style_context.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        self._setup_menu()
        self._setup_settings()
        self._setup_database()
        self._load_main_app()

        win.present()
        win.set_menu(self._menu)

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        loglevel = 3 if "loglevel" not in options else options["loglevel"]
        logger = pyot_logging.initialize(loglevel)
        logger.debug("Logger initialized.")

        self.activate()
        return 0

    def on_quit(self, action, param):
        self._window.on_quit()
        self.quit()

    def on_open_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window, on_response=self._load_file)
        dialog.show()

    def _load_file(self, dialog, response):
        if response != Gtk.ResponseType.ACCEPT:
            return

        try:
            filename = dialog.get_file().get_path()
            record = ParserFactory.make(filename).parse()
            activity = RecordProxy(record).to_activity()
            self._load_app(AppActivityInfo, {"activity": activity})
        except Exception as e:
            print(type(e))
            MessageDialogError(
                transient_for=self.get_window(),
                text=_(f"File {filename} cannot be opened: {e}"),
                title=_("Error opening a file")
            ).show()

    def get_pref(self, pref):
        return self._preferences.get_pref(pref)

    def get_pref_default(self, pref):
        return self._preferences.get_default(pref)

    def set_pref(self, pref, newvalue):
        self._preferences.set_pref(pref, newvalue)
        # if pref == AppPreferences.AUTO_IMPORT_FOLDER:
        #     self._auto_import()

    def get_window(self):
        return self._window

    def back_button_clicked(self, back_btn):
        """Close the current loaded app and then load the last loaded app"""
        self._apps_queue.pop()
        if not self._apps_queue:
            back_btn.hide()
            self._load_main_app()
            return
        if len(self._apps_queue) < 2:
            back_btn.hide()
        self._load_app(
            self._apps_queue[-1].class_var, self._apps_queue[-1].kwargs, self._apps_queue[-1].show_menu_buttons
        )

    def preferences_button_clicked(self, prefs_btn):
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                updated_prefs = dialog.get_updated_preferences()
                for pref, value in updated_prefs.items():
                    self.set_pref(pref, value)
            dialog.close()

        dialog = PreferencesDialog(parent=self._window, app=self)
        dialog.show()
        dialog.connect("response", on_response)

    def analytic_button_clicked(self, btn):
        self._load_app(AppAnalytic)

    def segments_button_clicked(self, btn):
        self._load_app(AppSegments, {"app": self})

    def open_external_app(self, class_var, dict_args):
        self._load_app(class_var, dict_args)

    def _load_main_app(self):
        self._load_app(AppActivityList, {"app": self}, True)

    def _load_app(self, class_var, kwargs: dict = dict({}), show_menu_buttons: bool = False):
        """Load external app whose class is class_var."""
        self._window.set_visibility_menu_buttons(show_menu_buttons)

        app_external = class_var(**kwargs)
        app_external.connect("actions-changed", self._connect_actions)
        self._connect_actions(app_external)

        if not list(filter(lambda al: al.class_var == class_var, self._apps_queue)):
            self._apps_queue.append(
                Application.AppLoaded(class_var, kwargs, app_external.get_actions(), show_menu_buttons)
            )

        self._window.load_app(app_external)
        if self._apps_queue and len(self._apps_queue) > 1:
            self._window.connect_action_button(PyopentracksWindow.ActionButton.BACK, self.back_button_clicked, None)

    def _connect_actions(self, app_external):
        self._window.disconnect_action_buttons()
        for action in app_external.get_actions():
            self._window.connect_action_button(action.button_id, action.callback, action.args)

    def _setup_menu(self):
        action = Gio.SimpleAction.new("import_folder", None)
        action.connect("activate", self._on_folder_import)
        self.add_action(action)

        action = Gio.SimpleAction.new("import_file", None)
        action.connect("activate", self._on_file_import)
        self.add_action(action)

        action = Gio.SimpleAction.new("export_all", None)
        action.connect("activate", self._on_export_all)
        self.add_action(action)

        action = Gio.SimpleAction.new("open_file", None)
        action.connect("activate", self.on_open_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_resource("/es/rgmf/pyopentracks/ui/menu.ui")
        self._menu = builder.get_object("app-menu")

    def _setup_settings(self):
        self._preferences = AppPreferences()

    def _setup_database(self):
        db = Database()
        migration = Migration(
            db,
            self._preferences.get_pref(AppPreferences.DB_VERSION)
        )
        db_version = migration.migrate()
        self._preferences.set_pref(AppPreferences.DB_VERSION, db_version)

    def _end_load_file_cb(self, gpxParserHandler):
        self._window.loading(1.0)

    def _on_folder_import(self, action, param):
        dialog = ImportFolderChooserWindow(parent=self._window, on_response=self._on_import)
        dialog.show()

    def _on_file_import(self, action, param):
        dialog = ImportFileChooserDialog(parent=self._window, on_response=self._on_import)
        dialog.show()

    def _on_import(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_file()
            import_dialog = ImportResultDialog(
                parent=self._window,
                filename=filename.get_path(),
                on_response_cb=self._on_import_response
            )
            import_dialog.show()

    def _on_import_response(self, dialog, response):
        if response == Gtk.ResponseType.DELETE_EVENT:
            self._load_main_app()

    def _on_export_all(self, action, param):
        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                folder = dialog.get_file().get_path()
                export_dialog = ExportResultDialog(parent=self._window, folder=folder)
                export_dialog.show()

        dialog = FolderChooserWindow(parent=self._window, on_response=on_response)
        dialog.show()
