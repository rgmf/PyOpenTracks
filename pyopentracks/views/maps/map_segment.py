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

from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import Champlain, GObject

from pyopentracks.models.database import Database


class MapSegment(Champlain.MarkerLayer, GObject.GObject):

    __gsignals__ = {
        "segment-ready": (GObject.SIGNAL_RUN_FIRST, None, (int, int))
    }

    def __init__(self):
        super().__init__()
        GObject.GObject.__init__(self)

        self._color_begin = Clutter.Color.new(0x00, 0x80, 0x00, 0xff)
        self._color_end = Clutter.Color.new(0x80, 0x00, 0x00, 0xff)

        self._marker_begin = None
        self._marker_end = None
        self._track_points = []

    def add_track_point(self, trackpoint):
        """Add the TrackPoint trackpoint.

        Arguments:
        trackpoint -- TrackPoint's object.
        """
        if not self._marker_begin:
            self._marker_begin = SegmentMarker.new_with_text(trackpoint, _("Start"), "Serif 10", None, self._color_begin)
            self._marker_begin.set_location(trackpoint.latitude, trackpoint.longitude)
            self.add_marker(self._marker_begin)
            return

        if not self._marker_end:
            self._marker_end = SegmentMarker.new_with_text(trackpoint, _("End"), "Serif 10", None, self._color_end)
        else:
            self._marker_end.set_trackpoint(trackpoint)

        if self._marker_end.less_than(self._marker_begin):
            return

        db = Database()
        self._track_points = db.get_track_points_between(self._marker_begin.get_trackpoint().id, self._marker_end.get_trackpoint().id)
        self.remove_all()
        self.add_marker(self._marker_begin)
        for tp in self._track_points:
            champlain_point = Champlain.Point.new()
            champlain_point.set_location(tp.latitude, tp.longitude)
            self.add_marker(champlain_point)

        self._marker_end.set_location(trackpoint.latitude, trackpoint.longitude)
        self.add_marker(self._marker_end)

        self.emit("segment-ready", self._marker_begin.get_trackpoint().id, self._marker_end.get_trackpoint().id)

    def clear(self):
        self.remove_all()
        self._marker_begin = None
        self._marker_end = None
        self._track_points = []


    def get_track_points(self):
        return self._track_points

class SegmentMarker(Champlain.Label):
    """
    It's a Champlain.Label with a TrackPoint's object.
    """

    def __init__(self):
        super().__init__()
        self._trackpoint = None

    @staticmethod
    def new_with_text(trackpoint, text, text_font, text_color, label_color):
        obj = SegmentMarker()
        obj._trackpoint = trackpoint
        obj.set_text(text)
        obj.set_font_name(text_font)
        obj.set_text_color(text_color)
        obj.set_color(label_color)
        return obj

    def get_trackpoint(self):
        return self._trackpoint

    def set_trackpoint(self, trackpoint):
        self._trackpoint = trackpoint

    def less_than(self, other):
        if not other:
            return True
        return self._trackpoint.id < other.get_trackpoint().id
