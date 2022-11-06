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
from abc import abstractmethod
from typing import List

from gi.repository import Gtk, GObject

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.location import Location
from pyopentracks.models.segment_point import SegmentPoint
from pyopentracks.models.track_point import TrackPoint
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.maps.base_map import BaseMap
from pyopentracks.views.maps.interactive_track_map import InteractiveTrackMap
from pyopentracks.views.maps.track_map import TrackMap


class MapLayout(Gtk.Box):
    """Base MapLayout.

    This class is used to add a champlain's map in a Gtk widget.
    """

    def __init__(self):
        super().__init__()
        self._map = self._build_map()

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self._map)
        self.pack_start(scrolled_window, False, True, 0)

        self.show_all()

    @abstractmethod
    def _build_map(self) -> BaseMap:
        pass

    @abstractmethod
    def add_polyline_from_points(self, points) -> None:
        pass


class SegmentMapLayout(MapLayout):
    """A MapLayout with a segment's polyline."""

    def __init__(self):
        super().__init__()

    def _build_map(self) -> BaseMap:
        return BaseMap()

    def add_polyline_from_points(self, points: List[SegmentPoint]) -> None:
        self._map.add_polyline([(p.latitude, p.longitude) for p in points])


class TrackMapLayout(MapLayout):
    """A MapLayout with a map with track points.

    When you create the map a label with a loading message is shown
    until you add the polyline.

    An interactive map can be asked so user can select segments.

    Signals:
    segment-selected -- this signal will be emitted when user select a segment.
    """

    def __init__(self):
        super().__init__()

    def _build_map(self) -> BaseMap:
        return TrackMap()

    def add_polyline_from_points(self, points: List[TrackPoint]) -> None:
        self._map.add_polyline(points)

    def add_polyline_from_activity_id(self, activity_id):
        """Load track points from activity's id."""
        ProcessView(self.add_polyline_from_points, DatabaseHelper.get_track_points, (activity_id,)).start()

    def highlight(self, locations: List[Location]):
        self._map.add_highlight_polyline(locations)

    def set_location_marker(self, location, tag):
        """Show a marker in the location with the tag."""
        self._map.set_location_marker(location, tag)


class TrackInteractiveMapLayout(MapLayout, GObject.GObject):
    """It's a MapLayout with interactive feature.

    It offers to the users the possibility of select a segment.
    """

    __gsignals__ = {
        "segment-selected": (GObject.SIGNAL_RUN_FIRST, None, (int, int))
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)

    def _build_map(self) -> BaseMap:
        map = InteractiveTrackMap()
        map.get_segment().connect("segment-ready", self._segment_ready_cb)
        return map

    def add_polyline_from_points(self, points: List[TrackPoint]) -> None:
        self._map.add_polyline(points)

    def get_segment(self):
        return self._map.get_segment()

    def reset(self):
        self._map.clear_segment()

    def _segment_ready_cb(self, segment, track_point_begin_id, track_point_end_id):
        """Call back executed when a MapSegment is selected and ready.

        Arguments:
        segment -- MapSegment object.
        track_point_begin_id -- begin segment TrackPoint's id property.
        track_point_end_id -- end's segment TrackPoint's id property.
        """
        self.emit("segment-selected", track_point_begin_id, track_point_end_id)
