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

from gi.repository import Gtk, Gio, Gdk

from pyopentracks.app_preferences import AppPreferences
from pyopentracks.io.gpx_parser import GpxParserHandlerInThread
from pyopentracks.app_window import PyopentracksWindow
from pyopentracks.views.file_chooser import (
    FileChooserWindow, FolderChooserWindow
)
from pyopentracks.models.migrations import Migration
from pyopentracks.models.database import Database
from pyopentracks.io.import_handler import (
    ImportHandler, ImportFileHandler, AutoImportHandler
)
from pyopentracks.views.dialogs import (
    MessageDialogError,
    ImportResultDialog,
    PreferencesDialog
)
from pyopentracks.app_analytic import AppAnalytic


class Application(Gtk.Application):
    def __init__(self, app_id):
        super().__init__(
            application_id=app_id,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self._menu: Gio.Menu = Gio.Menu()
        self._window: PyopentracksWindow = None
        self._preferences: AppPreferences = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self._setup_menu()
        self._setup_settings()
        self._setup_database()
        self._auto_import()

    def do_activate(self):
        stylecontext = Gtk.StyleContext()
        provider = Gtk.CssProvider()
        provider.load_from_resource(
            "/es/rgmf/pyopentracks/ui/gtk_style.css"
        )
        stylecontext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        win = self.props.active_window
        if not win:
            win = PyopentracksWindow(application=self)
            self._window = win
            win.set_menu(self._menu)
            self._load_tracks()
        win.present()

    def on_open_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.load_file(
                dialog.get_filename(), self._window.load_track_stats
            )
        dialog.destroy()

    def on_quit(self, action, param):
        self._window.on_quit()
        self.quit()

    def load_file(self, filename: str, cb):
        """Load the GPX filename and call cb.

        It loads track from GPX filename and call to the cb callback
        passing it th track object.

        Arguments:
        filename -- absolute path to a GPX file.
        cb -- the callback to call after loading.
        """
        self._window.loading(0.5)
        gpxParserHandle = GpxParserHandlerInThread()
        gpxParserHandle.connect("end-parse", self._end_load_file_cb)
        gpxParserHandle.parse(filename, cb)

    def back_button_clicked(self, back_btn):
        back_btn.hide()
        self._load_tracks()

    def preferences_button_clicked(self, prefs_btn):
        dialog = PreferencesDialog(parent=self._window, app=self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pass
        dialog.destroy()

    def analytic_button_clicked(self, btn):
        app_analytic = AppAnalytic()
        self._window.load_analytics(app_analytic.get_layout())

    def get_pref(self, pref):
        return self._preferences.get_pref(pref)

    def set_pref(self, pref, newvalue):
        self._preferences.set_pref(pref, newvalue)
        if pref == AppPreferences.AUTO_IMPORT_FOLDER:
            self._auto_import()

    def _setup_menu(self):
        action = Gio.SimpleAction.new("import_folder", None)
        action.connect("activate", self._on_import_folder)
        self.add_action(action)

        action = Gio.SimpleAction.new("import_file", None)
        action.connect("activate", self._on_import_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("open_file", None)
        action.connect("activate", self.on_open_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_resource(
            "/es/rgmf/pyopentracks/ui/menu.ui"
        )
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

    def _auto_import(self):
        folder = self._preferences.get_pref(AppPreferences.AUTO_IMPORT_FOLDER)
        if not folder:
            return
        AutoImportHandler().import_folder(folder, self._auto_import_new_tracks)

    def _auto_import_new_tracks(self):
        self._window.show_infobar(
            itype=Gtk.MessageType.QUESTION,
            message=_(
                "There are new tracks imported. "
                "Do you want to re-load all tracks to "
                "see the new ones?"
            ),
            buttons=[
                {
                    "text": _("Cancel"),
                    "cb": lambda b: self._window.clean_top_widget()
                },
                {
                    "text": _("Re-load"),
                    "cb": lambda b: self._load_tracks()
                }
            ]
        )

    def _load_tracks(self):
        db = Database()
        self._window.load_tracks(db.get_tracks())

    def _end_load_file_cb(self, gpxParserHandler):
        self._window.loading(1.0)

    def _on_import_folder(self, action, param):
        dialog = FolderChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            dialog.destroy()
            import_dialog = ImportResultDialog(
                parent=self._window,
                folder=folder
            )
            response = import_dialog.run()
            self._load_tracks()
            import_dialog.destroy()
        else:
            dialog.destroy()

    def _on_import_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._window.loading(0.5)
            handler = ImportFileHandler()
            handler.import_file(dialog.get_filename(), self._import_ended)
        dialog.destroy()

    def _import_ended(self, result: dict):
        """Called when file importing is finished.

        Arguments:
        result -- a dict with the following keys:
                  - file: file's path.
                  - import: the result.
                  - message: the message.
        """
        self._window.loading(1.0)
        if result["import"] == ImportHandler.OK:
            self._load_tracks()
        else:
            MessageDialogError(
                transient_for=self._window,
                text=(
                    _(f"Error importing the file {result['file']}") +
                    ": \n" + result["message"]
                ),
                title=_("Error importing track file")
            ).show()
