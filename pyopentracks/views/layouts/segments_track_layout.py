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


class SegmentsTrackLayout(Gtk.Box, GObject.GObject):

    __gsignals__ = {
        "segment-track-selected": (GObject.SIGNAL_RUN_FIRST, None, (int, int,))
    }

    def __init__(self, activity: Activity):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        GObject.GObject.__init__(self)

        self.get_style_context().add_class("pyot-bg")

        self._title_label = Gtk.Label.new(_("Segments"))
        self._title_label.set_wrap(True)
        self._title_label.set_margin_bottom(20)
        self._title_label.get_style_context().add_class("pyot-h2")

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(10)

        self.append(self._title_label)
        self.append(self._grid)

        self._data_rows = 0
        self._map = None
        self._activity: Activity = activity

    def build(self):
        activity_year = DateTimeUtils.date_from_timestamp(self._activity.start_time_ms).year
        segmentracks = DatabaseHelper.get_segment_tracks_by_activity_id(self._activity.id)
        if not segmentracks:
            self._grid.attach(Gtk.Label.new(_("There are not segments for this activity")), 0, 0, 1, 1)
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

    def _build_header_label(self, value, xalign=0.5, yalign=0.5, margin_top=0, margin_end=0, margin_bottom=0, margin_start=0):
        lbl = Gtk.Label.new(value)
        lbl.get_style_context().add_class("pyot-stats-small-header")
        lbl.set_xalign(xalign)
        lbl.set_yalign(yalign)
        lbl.set_margin_top(margin_top)
        lbl.set_margin_end(margin_end)
        lbl.set_margin_bottom(margin_bottom)
        lbl.set_margin_start(margin_start)
        return lbl

    def _build_info_box(self, segment_id, segment_track_id, name, distance, gain, slope):
        """Builds a box with information: name, distance, gain and slope values."""
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        btn_with_name = Gtk.Button.new_with_label(name)
        btn_with_name.connect("clicked", lambda w: self.emit("segment-track-selected", segment_id, segment_track_id))
        vbox.append(btn_with_name)

        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        distance_lbl = Gtk.Label.new(distance)
        distance_lbl.set_xalign(0.0)
        distance_lbl.set_yalign(0.5)
        gain_lbl = Gtk.Label.new(gain)
        gain_lbl.set_xalign(0.0)
        gain_lbl.set_yalign(0.5)
        slope_lbl = Gtk.Label.new(slope)
        slope_lbl.set_xalign(0.0)
        slope_lbl.set_yalign(0.5)
        hbox.append(distance_lbl)
        hbox.append(gain_lbl)
        hbox.append(slope_lbl)

        vbox.append(hbox)

        return vbox

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        label = Gtk.Label.new(value)
        label.set_xalign(0.0)
        label.set_yalign(0.5)
        box.append(label)
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
        label1 = Gtk.Label.new(value1[0])
        label1.set_xalign(0.0)
        label1.set_yalign(0.5)
        label2 = Gtk.Label.new(value1[1])
        label2.set_xalign(0.0)
        label2.set_yalign(0.5)
        hbox1.append(label1)
        hbox1.append(label2)

        hbox2 = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        label1 = Gtk.Label.new(value2[0])
        label1.set_xalign(0.0)
        label1.set_yalign(0.5)
        label2 = Gtk.Label.new(value2[1])
        label2.set_xalign(0.0)
        label2.set_yalign(0.5)
        hbox2.append(label1)
        hbox2.append(label2)

        vbox.append(hbox1)
        vbox.append(hbox2)

        return vbox

    def _build_pr_box(self, segment_track_record):
        if segment_track_record is None:
            box = Gtk.Box()
            image = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/gold-medal.svg")
            image.set_pixel_size(48)
            box.append(image)
            return box

        if segment_track_record.ranking == 2:
            widget = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/silver-medal.svg")
            widget.set_pixel_size(48)
        elif segment_track_record.ranking == 3:
            widget = Gtk.Image.new_from_resource("/es/rgmf/pyopentracks/icons/bronze-medal.svg")
            widget.set_pixel_size(48)
        else:
            widget = Gtk.Label.new(str(segment_track_record.ranking))
            widget.get_style_context().add_class("pyot-h2")

        vbox = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL)
        best_time_label = Gtk.Label.new(segment_track_record.best_time)

        vbox.append(best_time_label)
        vbox.append(widget)

        return vbox
