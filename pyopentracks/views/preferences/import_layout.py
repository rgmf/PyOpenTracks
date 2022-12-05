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

from gi.repository import Gtk

from pyopentracks.app_preferences import AppPreferences
from pyopentracks.views.file_chooser import FolderChooserWindow


class PreferencesImportLayout(Gtk.Box):

    def __init__(self, dialog):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._dialog = dialog

        self._title = Gtk.Label.new(_("Auto-import folder"))
        self._title.get_style_context().add_class("pyot-h3")
        self._title.set_halign(Gtk.Align.CENTER)
        self._title.set_margin_top(20)

        self._help_text = Gtk.Label.new(_(
            "Select a folder to import automatically new activity files. "
            "PyOpenTracks will check it for new files every time it opens."
        ))
        self._help_text.get_style_context().add_class("pyot-prefs-help")
        self._help_text.set_halign(Gtk.Align.CENTER)
        self._help_text.set_margin_bottom(20)

        self._content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._content_box.set_halign(Gtk.Align.CENTER)
        self._switch = Gtk.Switch()
        self._switch.set_valign(Gtk.Align.CENTER)
        auto_import_folder = dialog.get_pref(AppPreferences.AUTO_IMPORT_FOLDER)
        self._switch.set_active(auto_import_folder)
        self._switch.connect("notify::active", self._on_folder_pref_activated)
        self._select_folder_button = Gtk.Button.new_with_label(
            auto_import_folder if auto_import_folder else _("Select a folder...")
        )
        self._select_folder_button.set_sensitive(self._switch.get_active())
        self._select_folder_button.connect("clicked", self._on_select_folder_button_clicked)
        self._content_box.append(self._switch)
        self._content_box.append(self._select_folder_button)

        self.append(self._title)
        self.append(self._help_text)
        self.append(self._content_box)

    def _on_select_folder_button_clicked(self, button):
        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                folder_path = dialog.get_file().get_path()
                button.set_label(folder_path)
                self._dialog.set_pref(AppPreferences.AUTO_IMPORT_FOLDER, folder_path)

        dialog = FolderChooserWindow(parent=self._dialog, on_response=on_response)
        dialog.show()

    def _on_folder_pref_activated(self, switch, gparam):
        if switch.get_active():
            self._select_folder_button.set_sensitive(True)
            self._select_folder_button.set_sensitive(True)
        else:
            self._select_folder_button.set_sensitive(False)
            self._select_folder_button.set_label(_("Select a folder..."))
            self._dialog.set_pref(AppPreferences.AUTO_IMPORT_FOLDER, "")
