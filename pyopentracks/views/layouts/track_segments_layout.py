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
from pyopentracks.views.layouts.segments_list_layout import SegmentsListLayout
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_segments_layout.ui")
class TrackSegmentsLayout(Gtk.Box):
    __gtype_name__ = "TrackSegmentsLayout"

    _scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()

    def __init__(self, track):
        super().__init__()
        self.get_style_context().add_class("pyot-bg")
        self._track = track
        self._segments_layout = SegmentsListLayout.from_track(track)
        self._segments_layout.connect("segment-track-selected", self._segment_track_selected)
        self._map_layout = TrackMapLayout()

    def build(self):
        self._scrolled_window.add(self._segments_layout)
        self.pack_start(self._map_layout, True, True, 0)
        self._map_layout.add_polyline_from_trackid(self._track.id)
        self.show_all()

    def _segment_track_selected(self, widget, segment_id, segment_track_id):
        self._map_layout.highlight(
            [Location(sp.latitude, sp.longitude) for sp in DatabaseHelper.get_segment_points(segment_id)]
        )
