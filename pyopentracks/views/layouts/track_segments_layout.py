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
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.segments_track_layout import SegmentsTrackLayout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout
from pyopentracks.utils.utils import TrackPointUtils


class TrackSegmentsLayout(Gtk.Box, DataUpdateObserver, Layout):

    def __init__(self, activity):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        Layout.__init__(self)

        self._map_layout = None

        self.get_style_context().add_class("pyot-bg")

        self._refresh_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._refresh_info_box.set_margin_top(20)
        self._refresh_info_box.set_margin_bottom(20)
        self._refresh_info_box.set_margin_start(20)
        self._refresh_info_box.set_margin_end(20)
        self._refresh_button = Gtk.Button()
        self._refresh_button.set_icon_name("refresh-symbolic")
        self._refresh_button.connect("clicked", self._refresh)
        self._refresh_message_label = Gtk.Label.new(
            _("New segments have been created, refresh to see them (it can take a long time)")
        )
        self._refresh_info_box.append(self._refresh_button)
        self._refresh_info_box.append(self._refresh_message_label)
        self._refresh_info_box.hide()
        self._refresh_button.hide()
        self._refresh_message_label.hide()

        self._content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._content_box.set_vexpand(True)
        self._content_box.set_homogeneous(True)
        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.set_margin_top(20)
        self._scrolled_window.set_margin_bottom(20)
        self._scrolled_window.set_margin_start(20)
        self._scrolled_window.set_margin_end(20)
        self._content_box.append(self._scrolled_window)

        self.append(self._refresh_info_box)
        self.append(self._content_box)

        self._activity = activity

        self._segments_layout = SegmentsTrackLayout(activity)
        self._segments_layout.build()
        self._segments_layout.connect("segment-track-selected", self._segment_track_selected)

    def build(self):
        self._map_layout = TrackMapLayout()
        self._scrolled_window.set_child(self._segments_layout)
        self._content_box.append(self._map_layout)
        if self._activity.all_track_points:
            self._map_layout.add_polyline_from_points(TrackPointUtils.to_locations(self._activity.all_track_points))
        else:
            self._map_layout.add_polyline_from_activity_id(self._activity.id)

    def data_updated_notified(self):
        self._refresh_info_box.show()
        self._refresh_button.show()
        self._refresh_message_label.show()

    def _refresh(self, button):
        before_update_rows = self._segments_layout.get_number_rows()

        self._segments_layout = SegmentsTrackLayout(self._activity)
        self._segments_layout.build()
        self._segments_layout.connect("segment-track-selected", self._segment_track_selected)

        after_update_rows = self._segments_layout.get_number_rows()
        if after_update_rows > before_update_rows:
            self._refresh_info_box.hide()
            self._scrolled_window.set_child(self._segments_layout)

    def _segment_track_selected(self, widget, segment_id, segment_track_id):
        self._map_layout.highlight(
            [Location(sp.latitude, sp.longitude) for sp in DatabaseHelper.get_segment_points(segment_id)]
        )

