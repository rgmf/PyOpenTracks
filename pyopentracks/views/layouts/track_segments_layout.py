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

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.location import Location
from pyopentracks.observers.data_update_observer import DataUpdateObserver
from pyopentracks.views.layouts.segments_track_layout import SegmentsTrackLayout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_segments_layout.ui")
class TrackSegmentsLayout(Gtk.Box, DataUpdateObserver):
    __gtype_name__ = "TrackSegmentsLayout"

    _scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    _content_box: Gtk.Box = Gtk.Template.Child()
    _refresh_info_box: Gtk.Box = Gtk.Template.Child()
    _refresh_button: Gtk.Button = Gtk.Template.Child()
    _refresh_message_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, track):
        super().__init__()

        self.get_style_context().add_class("pyot-bg")
        self._track = track

        self._refresh_message_label.set_label(
            _("New segments have been created, refresh to see them (it can take a long time)")
        )
        self._refresh_button.connect("clicked", self._refresh)

        self._segments_layout = SegmentsTrackLayout(track)
        self._segments_layout.build()
        self._segments_layout.connect("segment-track-selected", self._segment_track_selected)
        self._map_layout = TrackMapLayout()

    def build(self):
        self._scrolled_window.add(self._segments_layout)
        self._content_box.pack_start(self._map_layout, True, True, 0)
        if self._track.all_track_points:
            self._map_layout.add_polyline_from_points(self._track.all_track_points)
        else:
            self._map_layout.add_polyline_from_trackid(self._track.id)
        self.show_all()

    def data_updated_notified(self):
        self._refresh_info_box.show()
        self._refresh_button.show()
        self._refresh_message_label.show()

    def _refresh(self, button):
        before_update_rows = self._segments_layout.get_number_rows()

        self._segments_layout = SegmentsTrackLayout(self._track)
        self._segments_layout.build()
        self._segments_layout.connect("segment-track-selected", self._segment_track_selected)

        after_update_rows = self._segments_layout.get_number_rows()
        if after_update_rows > before_update_rows:
            self._refresh_info_box.hide()
            for child in self._scrolled_window.get_children():
                self._scrolled_window.remove(child)
            self._scrolled_window.add(self._segments_layout)
            self.show_all()

    def _segment_track_selected(self, widget, segment_id, segment_track_id):
        self._map_layout.highlight(
            [Location(sp.latitude, sp.longitude) for sp in DatabaseHelper.get_segment_points(segment_id)]
        )
