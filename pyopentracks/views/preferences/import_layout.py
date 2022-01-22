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

from gi.repository import Gtk

from pyopentracks.app_preferences import AppPreferences


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/preferences_import_layout.ui")
class PreferencesImportLayout(Gtk.Box):
    __gtype_name__ = "PreferencesImportLayout"

    _title: Gtk.Label = Gtk.Template.Child()
    _help_text: Gtk.Label = Gtk.Template.Child()
    _content_box: Gtk.Box = Gtk.Template.Child()
    _switch: Gtk.Switch = Gtk.Template.Child()
    _file_chooser: Gtk.FileChooserButton = Gtk.Template.Child()

    def __init__(self, dialog):
        super().__init__()

        self._dialog = dialog

        self._title.set_text(_("Auto-import folder"))
        self._title.get_style_context().add_class("pyot-h3")

        self._help_text.set_text(_(
            "Select a folder to import automatically new track files. "
            "PyOpenTracks will check it for new files every time it opens."
        ))
        self._help_text.get_style_context().add_class("pyot-prefs-help")

        self._content_box.get_style_context().add_class("pyot-stats-bg-color")

        is_auto_import_set = dialog.get_pref(AppPreferences.AUTO_IMPORT_FOLDER)

        self._switch.set_active(is_auto_import_set)
        self._switch.connect("notify::active", self._on_folder_pref_activated)

        self._file_chooser.set_current_folder(is_auto_import_set)
        self._file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self._file_chooser.connect("file-set", self._on_folder_pref_changed)

    def _on_folder_pref_activated(self, switch, gparam):
        if switch.get_active():
            self._file_chooser.set_sensitive(True)
        else:
            self._file_chooser.set_sensitive(False)
            self._file_chooser.set_current_folder("")
            self._dialog.set_pref(AppPreferences.AUTO_IMPORT_FOLDER, "")

    def _on_folder_pref_changed(self, chooser):
        self._dialog.set_pref(
            AppPreferences.AUTO_IMPORT_FOLDER, chooser.get_filename()
        )
