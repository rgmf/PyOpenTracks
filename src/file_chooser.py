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


class FileChooserWindow(Gtk.FileChooserDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Select a track file")
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        self._add_filters()

    def _add_filters(self):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("GPX files")
        filter_text.add_mime_type("application/gpx+xml")
        self.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("KML files")
        filter_py.add_mime_type("application/vnd.google-earth.kml+xml")
        self.add_filter(filter_py)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("KMZ files")
        filter_py.add_mime_type("application/vnd.google-earth.kmz")
        self.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        self.add_filter(filter_any)
