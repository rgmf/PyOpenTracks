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

from dataclasses import dataclass
from typing import List

from pyopentracks.tasks.fit_segment import FitSegment
from pyopentracks.utils.utils import SanitizeFile
from pyopentracks.views.dialogs import (
    QuestionDialog,
    MessageDialogError,
    SegmentEditDialog
)
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.models.segment import Segment
from pyopentracks.views.file_chooser import ExportSegmentChooserWindow
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.track_map_layout import SegmentMapLayout


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segments_list_layout.ui")
class SegmentsListLayout(Gtk.Box):
    __gtype_name__ = "SegmentsListLayout"

    _top_box: Gtk.Box = Gtk.Template.Child()
    _box_header: Gtk.Box = Gtk.Template.Child()
    _title_label: Gtk.Label = Gtk.Template.Child()
    _combobox_segments: Gtk.ComboBox = Gtk.Template.Child()
    _button_delete: Gtk.Button = Gtk.Template.Child()
    _button_edit: Gtk.Button = Gtk.Template.Child()
    _button_export: Gtk.Button = Gtk.Template.Child()
    _segments_list_store: Gtk.ListStore = Gtk.Template.Child()
    _box_segment_detail: Gtk.Box = Gtk.Template.Child()
    _box_map: Gtk.Box = Gtk.Template.Child()
    _grid: Gtk.Grid = Gtk.Template.Child()

    @dataclass
    class SegmentData:
        segment: Segment
        segment_tracks: List[SegmentTrack]

    def __init__(self):
        super().__init__()

        self._data_rows = 0
        self._map = None

        self._button_export.set_label(_("Export to FIT"))

        self._button_delete.connect("clicked", self._button_delete_clicked_cb)
        self._button_edit.connect("clicked", self._button_edit_clicked_cb)
        self._button_export.connect("clicked", self._button_export_clicked_cb)

        self._label_segment_name = None

        self._title_label.set_text(_("Segments"))
        self._title_label.set_line_wrap(True)
        self._title_label.get_style_context().add_class("pyot-h2")

        self._box_segment_detail.get_style_context().add_class("pyot-stats-bg-color")

        self.get_style_context().add_class("pyot-bg")

        self._title_label.set_text(_("Loading segments..."))

    def build(self):
        ProcessView(self._on_data_ready, self._data_loading, None).start()

    def _on_segment_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            segmentid = self._segments_list_store[iter_item][0]
            self._title_label.set_text(_("Loading segments..."))
            ProcessView(self._on_data_ready, self._data_changing, (segmentid,)).start()

    def _data_loading(self):
        segments = DatabaseHelper.get_segments()
        if not segments:
            return None

        self._combobox_segments.set_wrap_width(2 if len(segments) > 10 else 1)
        for segment in segments:
            self._segments_list_store.append([segment.id, segment.name])
        self._combobox_segments.set_active(0)
        self._combobox_segments.connect("changed", self._on_segment_changed)

        return SegmentsListLayout.SegmentData(
            segments[0],
            DatabaseHelper.get_segment_tracks_by_segmentid(segments[0].id, True)
        )

    def _data_changing(self, segmentid):
        segment = DatabaseHelper.get_segment_by_id(segmentid)
        return SegmentsListLayout.SegmentData(
            segment,
            DatabaseHelper.get_segment_tracks_by_segmentid(segment.id, True)
        )

    def _on_data_ready(self, data: SegmentData):
        for w in self._grid.get_children():
            self._grid.remove(w)
        for w in self._box_segment_detail.get_children():
            self._box_segment_detail.remove(w)
        for w in self._box_map.get_children():
            self._box_map.remove(w)

        if not data:
            self._show_info_no_data()
            return

        self._button_delete.set_sensitive(True)
        self._button_edit.set_sensitive(True)
        self._button_export.set_sensitive(True)

        grid = Gtk.Grid()
        grid.attach(
            self._build_header_label(_("Name:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 0, 1, 1
        )
        self._label_segment_name = self._build_header_label(
            data.segment.name, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20
        )
        grid.attach(self._label_segment_name, 1, 0, 1, 1)
        grid.attach(
            self._build_header_label(_("Distance:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 1, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.distance, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 1, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Elevation Gain:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 2, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.gain, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 2, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Elevation Loss:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 3, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.loss, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 3, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Slope:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 4, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.slope, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 4, 1, 1
        )

        self._box_segment_detail.pack_start(grid, False, True, 0)

        map_layout = SegmentMapLayout()
        map_layout.add_polyline_from_points(DatabaseHelper.get_segment_points(data.segment.id))
        self._box_map.pack_start(map_layout, True, True, 0)

        top = 0

        self._grid.attach(Gtk.Label("#"), 0, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Time")), 1, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Speed")), 2, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Speed")), 3, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Heart Rate")), 4, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Heart Rate")), 5, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Cadence")), 6, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Cadence")), 7, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Activity Information")), 8, top, 1, 1)
        for i, st in enumerate(data.segment_tracks):
            top = top + 1
            self._grid.attach(Gtk.Label(str(i + 1)), 0, top, 1, 1)
            self._grid.attach(self._build_box(st.time), 1, top, 1, 1)
            self._grid.attach(self._build_box(st.avgspeed), 2, top, 1, 1)
            self._grid.attach(self._build_box(st.maxspeed), 3, top, 1, 1)
            self._grid.attach(self._build_box(st.avghr), 4, top, 1, 1)
            self._grid.attach(self._build_box(st.maxhr), 5, top, 1, 1)
            self._grid.attach(self._build_box(st.avgcadence), 6, top, 1, 1)
            self._grid.attach(self._build_box(st.maxcadence), 7, top, 1, 1)
            self._grid.attach(self._build_track_box(st.track), 8, top, 1, 1)
            self._data_rows = self._data_rows + 1

        self._title_label.set_text(_("Segments"))
        self.show_all()

    def get_number_rows(self):
        return self._data_rows

    def _show_info_no_data(self):
        for child in self.get_children():
            self.remove(child)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_start(50)
        box.set_margin_end(50)
        label1 = Gtk.Label(_("There are not anything to show"), xalign=0.0)
        label2 = Gtk.Label(_(
            "Go to track list, select one of them and create the segment you want clicking on the track you can "
            "see on the map. You have to add two points on the map: start and end segment."
        ), xalign=0.0)
        label1.get_style_context().add_class("pyot-h2")
        box.pack_start(label1, False, False, 10)
        box.pack_start(label2, False, False, 10)
        self.pack_start(box, False, False, 0)
        self.remove(self._top_box)
        self.show_all()

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

    def _build_track_box(self, track):
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        track_name = Gtk.Label(label=track.name, xalign=0.0, yalign=0.0)
        track_name.set_line_wrap(True)
        vbox.pack_start(track_name, True, True, 0)
        vbox.pack_start(Gtk.Label(label=track.stats.short_start_time, xalign=0.0, yalign=0.0), True, True, 0)
        return vbox

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        box.set_homogeneous(False)
        box.pack_start(Gtk.Label(label=value, xalign=0.0, yalign=0.0), True, True, 0)
        return box

    def _button_delete_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is None:
            MessageDialogError(
                transient_for=self.get_toplevel(),
                text=_("There are not any segment selected"),
                title=_("Error deleting a segment")
            ).show()
            return

        dialog = QuestionDialog(
            parent=self.get_toplevel(),
            title=_("Remove Segment"),
            question=_(f"Do you really want to remove the segment? This will remove all data about this segment.")
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.CANCEL:
            return

        segmentid = self._segments_list_store[iter_item][0]
        DatabaseHelper.delete(DatabaseHelper.get_segment_by_id(segmentid))
        self._title_label.set_text(_("Loading segments..."))
        self._button_delete.set_sensitive(False)
        self._button_edit.set_sensitive(False)
        self._button_export.set_sensitive(False)
        self._segments_list_store.clear()

        self._on_data_ready(self._data_loading())

    def _button_edit_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is not None:
            segmentid = self._segments_list_store[iter_item][0]
            dialog = SegmentEditDialog(parent=self.get_toplevel(), segment=DatabaseHelper.get_segment_by_id(segmentid))
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.OK:
                return

            segment = dialog.get_segment()
            self._segments_list_store.set_value(iter_item, 1, segment.name)
            if self._label_segment_name:
                self._label_segment_name.set_label(segment.name)
            DatabaseHelper.update(segment)

    def _button_export_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is None:
            return

        segment = DatabaseHelper.get_segment_by_id(self._segments_list_store[iter_item][0])
        fit_segment = FitSegment(segment).compute_binary()
        dialog = ExportSegmentChooserWindow(current_name=SanitizeFile.fit_file(segment.name))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(SanitizeFile.fit_file(dialog.get_filename()), "wb") as fd:
                fd.write(fit_segment)
        dialog.destroy()
