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

from .app_window import PyopentracksWindow
from .file_chooser import FileChooserWindow


MENU_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">app.open_file</attribute>
        <attribute name="label" translatable="yes">_Open file...</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""


class Application(Gtk.Application):
    def __init__(self, app_id):
        super().__init__(
            application_id=app_id,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self._menu: Gio.Menu = Gio.Menu()
        self._window: PyopentracksWindow = None

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PyopentracksWindow(application=self)
            self._window = win
            win.set_menu(self._menu)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("open_file", None)
        action.connect("activate", self.on_open_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self._menu = builder.get_object("app-menu")

    def on_open_file(self, action, param):
        dialog = FileChooserWindow(parent=self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked!")
            print("File Selected:", dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Open canceled!")
        dialog.destroy()

    def on_quit(self, action, param):
        self.quit()
