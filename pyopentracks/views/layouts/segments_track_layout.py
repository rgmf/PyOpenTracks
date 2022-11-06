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

from gi.repository import Gtk, GObject
from pyopentracks.models.activity import Activity

from pyopentracks.utils.utils import DateTimeUtils
from pyopentracks.models.database_helper import DatabaseHelper


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segments_track_layout.ui")
class SegmentsTrackLayout(Gtk.Box, GObject.GObject):
    __gtype_name__ = "SegmentsTrackLayout"

    __gsignals__ = {
        "segment-track-selected": (GObject.SIGNAL_RUN_FIRST, None, (int, int,))
    }

    _title_label: Gtk.Label = Gtk.Template.Child()
    _grid: Gtk.Grid = Gtk.Template.Child()

    def __init__(self, activity: Activity):
        super().__init__()
        GObject.GObject.__init__(self)

        self._data_rows = 0
        self._map = None
        self._activity: Activity = activity

        self._title_label.set_text(_("Segments"))
        self._title_label.set_line_wrap(True)
        self._title_label.get_style_context().add_class("pyot-h2")

        self.get_style_context().add_class("pyot-bg")

    def build(self):
        activity_year = DateTimeUtils.date_from_timestamp(self._activity.start_time_ms).year
        segmentracks = DatabaseHelper.get_segment_tracks_by_activity_id(self._activity.id)
        if not segmentracks:
            self._grid.attach(Gtk.Label(_("There are not segments for this activity")), 0, 0, 1, 1)
            return object

        self._grid.attach(self._build_header_label(_("Segment Information")), 0, 0, 1, 1)
        self._grid.attach(self._build_header_label(_("Time")), 1, 0, 1, 1)
        self._grid.attach(self._build_header_label(self._activity.stats.speed_label(self._activity.category)), 2, 0, 1, 1)
        self._grid.attach(self._build_header_label(_("Heart Rate")), 3, 0, 1, 1)
        self._grid.attach(self._build_header_label(_("Cadence")), 4, 0, 1, 1)
        self._grid.attach(self._build_header_label(_("All Times PR")), 5, 0, 1, 1)
        self._grid.attach(self._build_header_label(str(activity_year) + " PR"), 6, 0, 1, 1)

        for i, st in enumerate(segmentracks):
            all_times_pr = DatabaseHelper.get_segment_track_record(st.segmentid, st.time_ms)
            year_pr = DatabaseHelper.get_segment_track_record(st.segmentid, st.time_ms, activity_year)
            st.activity = self._activity
            segment = DatabaseHelper.get_segment_by_id(st.segmentid)
            self._grid.attach(
                self._build_info_box(
                    segment.id, st.id, segment.name, segment.distance, segment.gain, segment.slope
                ),
                0, i + 1, 1, 1
            )
            self._grid.attach(self._build_box(st.time), 1, i + 1, 1, 1)
            self._grid.attach(
                self._build_box_2((_("Avg.:"), st.avgspeed), (_("Max.:"), st.maxspeed)),
                2, i + 1, 1, 1
            )
            self._grid.attach(
                self._build_box_2((_("Avg.:"), st.avghr), (_("Max.:"), st.maxhr)),
                3, i + 1, 1, 1
            )
            self._grid.attach(
                self._build_box_2((_("Avg.:"), st.avgcadence), (_("Max.:"), st.maxcadence)),
                4, i + 1, 1, 1
            )
            self._grid.attach(self._build_pr_box(all_times_pr), 5, i + 1, 1, 1)
            self._grid.attach(self._build_pr_box(year_pr), 6, i + 1, 1, 1)
            self._data_rows = self._data_rows + 1
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

    def _build_info_box(self, segment_id, segment_track_id, name, distance, gain, slope):
        """Builds a box with information: name, distance, gain and slope values."""
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        btn_with_name = Gtk.Button(name)
        btn_with_name.set_relief(Gtk.ReliefStyle.NONE)
        btn_with_name.connect("clicked", lambda w: self.emit("segment-track-selected", segment_id, segment_track_id))
        vbox.pack_start(btn_with_name, True, True, 0)

        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(Gtk.Label(label=distance, xalign=0.0, yalign=0.0), True, True, 0)
        hbox.pack_start(Gtk.Label(label=gain, xalign=0.0, yalign=0.0), True, True, 0)
        hbox.pack_start(Gtk.Label(label=slope, xalign=0.0, yalign=0.0), True, True, 0)

        vbox.pack_start(hbox, True, True, 0)

        return vbox

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        box.set_homogeneous(False)
        box.pack_start(Gtk.Label(label=value, xalign=0.0, yalign=0.0), True, True, 0)
        return box

    def _build_box_2(self, value1: tuple, value2: tuple):
        """Builds a box with two values.

        Arguments:
        value1 - tuple with label and value.
        value2 - tuple with label and value.
        """
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)

        hbox1 = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox1.pack_start(Gtk.Label(label=value1[0], xalign=0.0, yalign=0.0), True, True, 0)
        hbox1.pack_start(Gtk.Label(label=value1[1], xalign=0.0, yalign=0.0), True, True, 0)

        hbox2 = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox2.pack_start(Gtk.Label(label=value2[0], xalign=0.0, yalign=0.0), True, True, 0)
        hbox2.pack_start(Gtk.Label(label=value2[1], xalign=0.0, yalign=0.0), True, True, 0)

        vbox.pack_start(hbox1, True, True, 0)
        vbox.pack_start(hbox2, True, True, 0)

        return vbox

    def _build_pr_box(self, segment_track_record):
        if segment_track_record is None:
            return Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/gold-medal.svg")

        if segment_track_record.ranking == 2:
            widget = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/silver-medal.svg")
        elif segment_track_record.ranking == 3:
            widget = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/bronze-medal.svg")
        else:
            widget = Gtk.Label(segment_track_record.ranking)
            widget.get_style_context().add_class("pyot-h2")

        vbox = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL)
        best_time_label = Gtk.Label(segment_track_record.best_time)

        vbox.pack_start(best_time_label, True, True, 0)
        vbox.pack_start(widget, True, True, 0)

        return vbox
