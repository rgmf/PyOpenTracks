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
import os

from gi.repository import Gtk, Gio

from pyopentracks.app_preferences import AppPreferences


class CustomFileChooserDialog:
    def __init__(self, title, parent, action, accept_label, cancel_label, on_response):
        self._on_response_cb = on_response
        self._preferences = AppPreferences()
        self._current_folder = self._preferences.get_pref(AppPreferences.LAST_FOLDER)
        self._dialog = Gtk.FileChooserNative.new(
            title=title,
            parent=parent,
            action=action,
            accept_label=accept_label,
            cancel_label=cancel_label
        )
        if self._current_folder and os.path.isdir(self._current_folder):
            self._dialog.set_current_folder(Gio.File.new_for_path(self._current_folder))
        self._dialog.connect("response", self._on_response)

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder = os.path.dirname(dialog.get_file().get_path())
            self._preferences.set_pref(AppPreferences.LAST_FOLDER, "" if folder is None else folder)
        self._on_response_cb(dialog, response)

    def show(self):
        self._dialog.show()

    def set_current_name(self, name):
        self._dialog.set_current_name(name)

    def add_filter(self, filter):
        self._dialog.add_filter(filter)

    def set_do_overwrite_confirmation(self, value: bool):
        self._dialog.set_do_overwrite_confirmation(value)

    @property
    def current_folder(self):
        return self._current_folder


class ImportFileChooserDialog(CustomFileChooserDialog):
    def __init__(self, parent, on_response):
        super().__init__(
            _("Select a track file"),
            parent,
            Gtk.FileChooserAction.OPEN,
            _("Import"),
            _("Cancel"),
            on_response=on_response
        )
        self._add_filters()

    def _add_filters(self):
        filter_gpx_fit = Gtk.FileFilter()
        filter_gpx_fit.set_name(_("GPX and FIT files"))
        filter_gpx_fit.add_mime_type("application/gpx+xml")
        filter_gpx_fit.add_pattern("*.fit")
        self.add_filter(filter_gpx_fit)

        filter_only_gpx = Gtk.FileFilter()
        filter_only_gpx.set_name(_("GPX files"))
        filter_only_gpx.add_mime_type("application/gpx+xml")
        self.add_filter(filter_only_gpx)

        filter_only_fit = Gtk.FileFilter()
        filter_only_fit.set_name(_("FIT files"))
        filter_only_fit.add_pattern("*.fit")
        self.add_filter(filter_only_fit)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(_("Any files"))
        filter_any.add_pattern("*")
        self.add_filter(filter_any)


class ImportFolderChooserWindow(CustomFileChooserDialog):
    def __init__(self, parent, on_response):
        super().__init__(
            _("Select a folder"),
            parent,
            Gtk.FileChooserAction.SELECT_FOLDER,
            _("Import Folder"),
            _("Cancel"),
            on_response
        )


class ExportSegmentChooserDialog(CustomFileChooserDialog):
    def __init__(self, parent, on_response, current_name=_("Untitled.fit")):
        super().__init__(
            _("Export Segment FIT File"),
            parent,
            Gtk.FileChooserAction.SAVE,
            _("Export"),
            _("Cancel"),
            on_response
        )
        self.set_current_name(current_name)


class FileChooserWindow(CustomFileChooserDialog):
    def __init__(self, parent, on_response):
        super().__init__(
            _("Select a file"),
            parent,
            Gtk.FileChooserAction.OPEN,
            _("Ok"),
            _("Cancel"),
            on_response
        )
        self._add_filters()

    def _add_filters(self):
        filter_gpx_fit = Gtk.FileFilter()
        filter_gpx_fit.set_name(_("GPX and FIT files"))
        filter_gpx_fit.add_mime_type("application/gpx+xml")
        filter_gpx_fit.add_pattern("*.fit")
        self.add_filter(filter_gpx_fit)

        filter_only_gpx = Gtk.FileFilter()
        filter_only_gpx.set_name(_("GPX files"))
        filter_only_gpx.add_mime_type("application/gpx+xml")
        self.add_filter(filter_only_gpx)

        filter_only_fit = Gtk.FileFilter()
        filter_only_fit.set_name(_("FIT files"))
        filter_only_fit.add_pattern("*.fit")
        self.add_filter(filter_only_fit)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(_("Any files"))
        filter_any.add_pattern("*")
        self.add_filter(filter_any)


class FolderChooserWindow(CustomFileChooserDialog):
    def __init__(self, parent, on_response):
        super().__init__(
            _("Select a folder"),
            parent,
            Gtk.FileChooserAction.SELECT_FOLDER,
            _("Ok"),
            _("Cancel"),
            on_response
        )
