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


class FileChooserWindow(Gtk.FileChooserDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_("Select a track file"))
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
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

        # filter_py = Gtk.FileFilter()
        # filter_py.set_name(_("KML files"))
        # filter_py.add_mime_type("application/vnd.google-earth.kml+xml")
        # self.add_filter(filter_py)
        #
        # filter_py = Gtk.FileFilter()
        # filter_py.set_name(_("KMZ files"))
        # filter_py.add_mime_type("application/vnd.google-earth.kmz")
        # self.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(_("Any files"))
        filter_any.add_pattern("*")
        self.add_filter(filter_any)


class FolderChooserWindow(Gtk.FileChooserDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_("Select a folder"))
        self.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )


class ExportSegmentChooserWindow(Gtk.FileChooserDialog):
    def __init__(self, current_name=_("Untitled.fit"), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_("Export Segment FIT File..."))
        self.set_action(Gtk.FileChooserAction.SAVE)
        self.set_current_name(current_name)
        self.set_do_overwrite_confirmation(True)
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE_AS,
            Gtk.ResponseType.OK,
        )
