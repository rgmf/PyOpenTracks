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

from pyopentracks.io.gpx_parser import GpxParserHandle

from gi.repository import Gtk, Gio, Gdk

from pyopentracks.app_window import PyopentracksWindow
from pyopentracks.views.file_chooser import FileChooserWindow, FolderChooserWindow
from pyopentracks.models.migrations import Migration
from pyopentracks.models.database import Database


class Application(Gtk.Application):
    def __init__(self, app_id):
        super().__init__(
            application_id=app_id,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self._menu: Gio.Menu = Gio.Menu()
        self._window: PyopentracksWindow = None
        self._settings: Gtk.Settings = None

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
            self._load_folder()
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self._setup_menu()
        self._setup_settings()
        self._setup_database()

    def on_import_folder(self, action, param):
        dialog = FolderChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._settings.set_string("trackspath", dialog.get_filename())
        dialog.destroy()

    def on_import_file(self, action, param):
        pass

    def on_open_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.load_file(dialog.get_filename(), self._window.load_track_stats)
        dialog.destroy()

    def on_quit(self, action, param):
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
        gpxParserHandle = GpxParserHandle()
        gpxParserHandle.connect("end-parse", self._end_parse_cb)
        gpxParserHandle.parse(filename, cb)

    def _setup_menu(self):
        action = Gio.SimpleAction.new("import_folder", None)
        action.connect("activate", self.on_import_folder)
        self.add_action(action)

        action = Gio.SimpleAction.new("import_file", None)
        action.connect("activate", self.on_import_file)
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
        self._settings = Gio.Settings.new("es.rgmf.pyopentracks")
        self._settings.connect(
            "changed::trackspath", self._on_settings_folder_changed
        )

    def _setup_database(self):
        db = Database()
        if "dbversion" in self._settings.keys():
            migration = Migration(db, self._settings.get_int("dbversion"))
        else:
            migration = Migration(db, None)
        db_version = migration.migrate()
        self._settings.set_int("dbversion", db_version)

    def _on_settings_folder_changed(self, settings, key):
        self._load_folder()

    def _load_folder(self):
        self._window.load_tracks_folder(
            self._settings.get_value("trackspath").get_string()
        )

    def _end_parse_cb(self, gpxParserHandle):
        self._window.loading(1.0)
