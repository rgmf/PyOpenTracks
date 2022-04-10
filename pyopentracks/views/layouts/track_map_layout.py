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

from typing import List

from gi.repository import Gtk, GObject

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.location import Location
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.maps.interactive_track_map import InteractiveTrackMap
from pyopentracks.views.maps.track_map import TrackMap


class TrackMapLayout(Gtk.Box, GObject.GObject):
    """A Gtk.VBox with a map with track points.

    When you create the map a label with a loading message is shown
    until you add the polyline.

    An interactive map can be asked so user can select segments.

    Signals:
    segment-selected -- this signal will be emitted when user select a segment.
    """

    __gsignals__ = {
        "segment-selected": (GObject.SIGNAL_RUN_FIRST, None, (int, int))
    }

    def __init__(self, interactive=False):
        super().__init__()
        GObject.GObject.__init__(self)

        if not interactive:
            self._map = TrackMap()
        else:
            self._map = InteractiveTrackMap()
            self._map.get_segment().connect("segment-ready", self._segment_ready_cb)

        self._is_interactive_map = interactive

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.pack_start(Gtk.Label(_("Loading map...")), False, True, 0)

        self.show_all()

    def add_polyline_from_trackid(self, trackid):
        """Load track points from track's id."""
        ProcessView(self.add_polyline_from_points, DatabaseHelper.get_track_points, (trackid,)).start()

    def add_polyline_from_points(self, track_points):
        """Add a polyline to the map using track_points."""
        self._map.add_polyline(track_points)
        for child in self.get_children():
            self.remove(child)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self._map)
        self.pack_start(scrolled_window, False, True, 0)
        self.show_all()

    def highlight(self, locations: List[Location]):
        self._map.add_highlight_polyline(locations)

    def set_location_marker(self, location, tag):
        """Show a marker in the location with the tag."""
        self._map.set_location_marker(location, tag)

    def get_segment(self):
        """Return the segment if it's ant interactive map. Otherwise, return None."""
        return None if not self._is_interactive_map else self._map.get_segment()

    def reset(self):
        if self._is_interactive_map:
            self._map.clear_segment()

    def _segment_ready_cb(self, segment, track_point_begin_id, track_point_end_id):
        """Call back executed when a MapSegment is selected and ready.

        Arguments:
        segment -- MapSegment object.
        track_point_begin_id -- begin segment TrackPoint's id property.
        track_point_end_id -- end's segment TrackPoint's id property.
        """
        self.emit("segment-selected", track_point_begin_id, track_point_end_id)
