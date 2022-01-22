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

from gi.repository import Gtk, Gio, Gdk, GLib

from pyopentracks.utils import logging as pyot_logging
from pyopentracks.app_preferences import AppPreferences
from pyopentracks.io.gpx_parser import GpxParserHandlerInThread
from pyopentracks.app_window import PyopentracksWindow
from pyopentracks.views.file_chooser import (
    FileChooserWindow, FolderChooserWindow
)
from pyopentracks.models.migrations import Migration
from pyopentracks.models.database import Database
from pyopentracks.io.import_handler import (
    ImportFileHandler, AutoImportHandler
)
from pyopentracks.views.preferences.dialog import PreferencesDialog
from pyopentracks.views.dialogs import (
    MessageDialogError,
    ImportResultDialog,
    ExportResultDialog
)
from pyopentracks.app_analytic import AppAnalytic
from pyopentracks.app_segments import AppSegments


class Application(Gtk.Application):
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

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        stylecontext = Gtk.StyleContext()
        provider = Gtk.CssProvider()
        provider.load_from_resource("/es/rgmf/pyopentracks/ui/gtk_style.css")
        stylecontext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        win = self.props.active_window
        if not win:
            win = PyopentracksWindow(application=self)
        self._window = win
        self._setup_menu()
        self._setup_settings()
        self._setup_database()
        self._load_tracks()
        self._auto_import()
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

    def on_open_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.load_file(dialog.get_filename(), self._window.load_track_stats)
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
            updated_prefs = dialog.get_updated_preferences()
            for p in updated_prefs:
                self.set_pref(p["pref"], p["value"])
        dialog.destroy()

    def analytic_button_clicked(self, btn):
        app_analytic = AppAnalytic()
        self._window.load_app(app_analytic)

    def segments_button_clicked(self, btn):
        app_segments = AppSegments()
        self._window.load_app(app_segments)

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

    def _auto_import(self):
        folder = self._preferences.get_pref(AppPreferences.AUTO_IMPORT_FOLDER)
        if not folder:
            return
        handler = AutoImportHandler()
        if self._preferences.get_pref(AppPreferences.OPENTRACKS_GAIN_LOSS_FILTER):
            handler.with_opentracks_gain_loss_correction()
        handler.connect("total-files-to-autoimport", self._auto_import_importing)
        handler.import_folder(folder, self._auto_import_new_tracks)

    def _auto_import_importing(self, handler: AutoImportHandler, total_files):
        if total_files == 0:
            return
        self._window.show_infobar(
            itype=Gtk.MessageType.INFO,
            message=_(f"{total_files} new tracks. Importing them..."),
            buttons=[]
        )

    def _auto_import_new_tracks(self):
        self._window.clean_top_widget()
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
            if self._preferences.get_pref(AppPreferences.OPENTRACKS_GAIN_LOSS_FILTER):
                import_dialog.with_opentracks_gain_loss_correction()
            import_dialog.run()
            import_dialog.destroy()
            self._load_tracks()
        else:
            dialog.destroy()

    def _on_import_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._window.loading(0.5)
            handler = ImportFileHandler(dialog.get_filename(), self._import_ended)
            if self._preferences.get_pref(AppPreferences.OPENTRACKS_GAIN_LOSS_FILTER):
                handler.with_opentracks_gain_loss_correction()
            handler.run()
        dialog.destroy()

    def _import_ended(self, result):
        """Called when file importing is finished.

        Arguments:
        result -- pyopentracks.io.result.Result object.
        """
        self._window.loading(1.0)
        if result.is_ok:
            self._load_tracks()
        else:
            MessageDialogError(
                transient_for=self._window,
                text=(
                    _(f"Error importing the file {result.filename}") +
                    ": \n" + result.message
                ),
                title=_("Error importing track file")
            ).show()

    def _on_export_all(self, action, param):
        dialog = FolderChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            dialog.destroy()
            export_dialog = ExportResultDialog(parent=self._window, folder=folder)
            export_dialog.run()
            export_dialog.destroy()
        else:
            dialog.destroy()
