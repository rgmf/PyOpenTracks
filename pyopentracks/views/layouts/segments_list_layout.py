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

from pyopentracks.models.database_helper import DatabaseHelper


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segments_list_layout.ui")
class SegmentsListLayout(Gtk.Box):
    __gtype_name__ = "SegmentsListLayout"

    _title_label: Gtk.Label = Gtk.Template.Child()
    _grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._data_rows = 0

        self._title_label.set_text(_("Segments"))
        self._title_label.set_line_wrap(True)
        self._title_label.set_margin_top(20)
        self._title_label.set_margin_left(20)
        self._title_label.get_style_context().add_class("pyot-h2")

        self.get_style_context().add_class("pyot-bg")

    @staticmethod
    def from_trackid(trackid):
        object = SegmentsListLayout()
        segmentracks = DatabaseHelper.get_segment_tracks_by_trackid(trackid)
        if not segmentracks:
            return object

        object._grid.attach(object._build_header_label(_("Segment Information")), 0, 0, 1, 1)
        object._grid.attach(object._build_header_label(_("Time")), 1, 0, 1, 1)
        object._grid.attach(object._build_header_label(_("Speed")), 2, 0, 1, 1)
        object._grid.attach(object._build_header_label(_("Heart Rate")), 3, 0, 1, 1)
        object._grid.attach(object._build_header_label(_("Cadence")), 4, 0, 1, 1)

        for i, st in enumerate(segmentracks):
            segment = DatabaseHelper.get_segment_by_id(st.segmentid)
            object._grid.attach(
                object._build_info_box(segment.name, segment.distance, segment.gain, segment.slope),
                0, i + 1, 1, 1)
            object._grid.attach(object._build_box(st.time), 1, i + 1, 1, 1)
            object._grid.attach(object._build_box(st.avgspeed), 2, i + 1, 1, 1)
            object._grid.attach(object._build_box(st.avghr), 3, i + 1, 1, 1)
            object._grid.attach(object._build_box(st.avgcadence), 4, i + 1, 1, 1)
            object._data_rows = object._data_rows + 1
        return object

    @staticmethod
    def from_segments():
        object = SegmentsListLayout()
        segments_list = DatabaseHelper.get_segment_tracks()
        top = 0
        for value in segments_list:
            segment = value["segment"]

            object._grid.attach(
                object._build_header_label(segment.name, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
                0, top, 4, 1
            )
            object._grid.attach(
                object._build_header_label(segment.distance, xalign=0.0, margin_top=20, margin_bottom=10),
                4, top, 1, 1
            )
            object._grid.attach(
                object._build_header_label(segment.gain, xalign=0.0, margin_top=20, margin_bottom=10),
                5, top, 1, 1
            )
            object._grid.attach(
                object._build_header_label(segment.slope, xalign=0.0, margin_top=20, margin_bottom=10),
                6, top, 1, 1
            )

            top = top + 1

            object._grid.attach(Gtk.Label(_("Time")), 0, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Avg. Speed")), 1, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Max. Speed")), 2, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Avg. Heart Rate")), 3, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Max. Heart Rate")), 4, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Avg. Cadence")), 5, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Max. Cadence")), 6, top, 1, 1)
            object._grid.attach(Gtk.Label(_("Activity Information")), 7, top, 1, 1)
            for st in value["segmentracks"]:
                top = top + 1
                object._grid.attach(object._build_box(st.time), 0, top, 1, 1)
                object._grid.attach(object._build_box(st.avgspeed), 1, top, 1, 1)
                object._grid.attach(object._build_box(st.maxspeed), 2, top, 1, 1)
                object._grid.attach(object._build_box(st.avghr), 3, top, 1, 1)
                object._grid.attach(object._build_box(st.maxhr), 4, top, 1, 1)
                object._grid.attach(object._build_box(st.avgcadence), 5, top, 1, 1)
                object._grid.attach(object._build_box(st.maxcadence), 6, top, 1, 1)
                object._grid.attach(object._build_track_box(DatabaseHelper.get_track_by_id(st.trackid)), 7, top, 1, 1)
                object._data_rows = object._data_rows + 1
            top = top + 1

        return object

    def get_number_rows(self):
        return self._data_rows

    def _build_header_label(self, value, xalign=0.5, yalign=0.5, margin_top=0, margin_right=0, margin_bottom=0, margin_left=0):
        lbl = Gtk.Label(value)
        lbl.get_style_context().add_class("pyot-stats-small-header")
        lbl.set_xalign(xalign)
        lbl.set_yalign(yalign)
        lbl.set_margin_top(margin_top)
        lbl.set_margin_right(margin_right)
        lbl.set_margin_bottom(margin_bottom)
        lbl.set_margin_left(margin_left)
        return lbl

    def _build_info_box(self, name, distance, gain, slope):
        """Builds a box with information: name, distance, gain and slope values."""
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        vbox.pack_start(Gtk.Label(label=name, xalign=0.0, yalign=0.0), True, True, 0)

        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(Gtk.Label(label=distance, xalign=0.0, yalign=0.0), True, True, 0)
        hbox.pack_start(Gtk.Label(label=gain, xalign=0.0, yalign=0.0), True, True, 0)
        hbox.pack_start(Gtk.Label(label=slope, xalign=0.0, yalign=0.0), True, True, 0)

        vbox.pack_start(hbox, True, True, 0)

        return vbox

    def _build_track_box(self, track):
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        track_name = Gtk.Label(label=track.name, xalign=0.0, yalign=0.0)
        track_name.set_line_wrap(True)
        vbox.pack_start(track_name, True, True, 0)
        vbox.pack_start(Gtk.Label(label=track.short_start_time, xalign=0.0, yalign=0.0), True, True, 0)
        return vbox

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        box.set_homogeneous(False)
        box.pack_start(Gtk.Label(label=value, xalign=0.0, yalign=0.0), True, True, 0)
        return box
