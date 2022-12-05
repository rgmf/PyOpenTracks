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
from pyopentracks.utils.utils import (
    SanitizeFile,
    SegmentPointUtils
)
from pyopentracks.views.dialogs import (
    QuestionDialog,
    MessageDialogError,
    SegmentEditDialog
)
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.segment_track import SegmentTrack
from pyopentracks.models.segment import Segment
from pyopentracks.views.file_chooser import ExportSegmentChooserDialog
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.track_map_layout import TrackMapLayout


class SegmentsListLayout(Gtk.Box):

    @dataclass
    class SegmentData:
        segment: Segment
        segment_tracks: List[SegmentTrack]

    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20, homogeneous=True)
        self.get_style_context().add_class("pyot-bg")

        self._app = app

        self._data_rows = 0
        self._map = None
        self._label_segment_name = None

        self._top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20, homogeneous=True)
        self.set_vexpand(True)

        self._box_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._box_header.set_margin_top(20)
        self._box_header.set_margin_start(20)

        self._box_header_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self._title_label = Gtk.Label.new(_("Segments"))
        self._title_label.set_wrap(True)
        self._title_label.get_style_context().add_class("pyot-h2")
        self._segments_list_store = Gtk.ListStore.new([int, str])
        renderer = Gtk.CellRendererText()
        self._combobox_segments = Gtk.ComboBox.new_with_model(self._segments_list_store)
        self._combobox_segments.pack_start(renderer, True)
        self._combobox_segments.add_attribute(renderer, "text", 1)
        self._box_header_top.append(self._title_label)
        self._box_header_top.append(self._combobox_segments)

        self._box_header_bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self._button_edit = Gtk.Button.new_with_label(_("Edit"))
        self._button_delete = Gtk.Button.new_with_label(_("Delete"))
        self._button_export = Gtk.Button.new_with_label(_("Export to FIT"))
        self._button_delete.connect("clicked", self._button_delete_clicked_cb)
        self._button_edit.connect("clicked", self._button_edit_clicked_cb)
        self._button_export.connect("clicked", self._button_export_clicked_cb)
        self._box_header_bottom.append(self._button_edit)
        self._box_header_bottom.append(self._button_delete)
        self._box_header_bottom.append(self._button_export)

        self._box_segment_detail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._box_segment_detail.set_vexpand(True)
        self._box_segment_detail.get_style_context().add_class("pyot-stats-bg-color")

        self._box_header.append(self._box_header_top)
        self._box_header.append(self._box_header_bottom)
        self._box_header.append(self._box_segment_detail)

        self._box_map = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._box_map.set_vexpand(True)

        self._top_box.append(self._box_header)
        self._top_box.append(self._box_map)

        self._grid = Gtk.Grid()
        self._grid.set_valign(Gtk.Align.START)
        self._grid.set_column_spacing(10)
        self._grid.set_row_spacing(10)
        self._grid.set_margin_start(20)
        self._grid.set_margin_end(20)
        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.set_child(self._grid)

        self.append(self._top_box)
        self.append(self._scrolled_window)

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

        for segment in segments:
            self._segments_list_store.append([segment.id, segment.name])
        self._combobox_segments.set_active(0)
        self._combobox_segments.connect("changed", self._on_segment_changed)

        return SegmentsListLayout.SegmentData(
            segments[0],
            DatabaseHelper.get_segment_tracks_by_segment_id(segments[0].id, True)
        )

    def _data_changing(self, segmentid):
        segment = DatabaseHelper.get_segment_by_id(segmentid)
        return SegmentsListLayout.SegmentData(
            segment,
            DatabaseHelper.get_segment_tracks_by_segment_id(segment.id, True)
        )

    def _on_data_ready(self, data: SegmentData):
        child = self._grid.get_first_child()
        while child is not None:
            self._grid.remove(child)
            child = self._grid.get_first_child()

        child = self._box_segment_detail.get_first_child()
        while child is not None:
            self._box_segment_detail.remove(child)
            child = self._box_segment_detail.get_first_child()

        child = self._box_map.get_first_child()
        while child is not None:
            self._box_map.remove(child)
            child = self._box_map.get_first_child()

        if not data:
            self._show_info_no_data()
            return

        self._button_delete.set_sensitive(True)
        self._button_edit.set_sensitive(True)
        self._button_export.set_sensitive(True)

        grid = Gtk.Grid()
        grid.attach(
            self._build_header_label(_("Name:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            0, 0, 1, 1
        )
        self._label_segment_name = self._build_header_label(
            data.segment.name, xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20
        )
        grid.attach(self._label_segment_name, 1, 0, 1, 1)
        grid.attach(
            self._build_header_label(_("Distance:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            0, 1, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.distance, xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            1, 1, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Elevation Gain:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            0, 2, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.gain, xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            1, 2, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Elevation Loss:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            0, 3, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.loss, xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            1, 3, 1, 1
        )
        grid.attach(
            self._build_header_label(_("Slope:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            0, 4, 1, 1
        )
        grid.attach(
            self._build_header_label(data.segment.slope, xalign=0.0, margin_top=20, margin_bottom=10, margin_start=20),
            1, 4, 1, 1
        )

        self._box_segment_detail.append(grid)

        map_layout = TrackMapLayout()
        map_layout.add_polyline_from_points(SegmentPointUtils.to_locations(DatabaseHelper.get_segment_points(data.segment.id)))
        map_layout.set_vexpand(True)
        self._box_map.append(map_layout)

        row = 0

        self._grid.attach(Gtk.Label.new("#"), 0, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Time")), 1, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Avg. Speed")), 2, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Max. Speed")), 3, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Avg. Heart Rate")), 4, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Max. Heart Rate")), 5, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Avg. Cadence")), 6, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Max. Cadence")), 7, row, 1, 1)
        self._grid.attach(Gtk.Label.new(_("Activity Information")), 8, row, 1, 1)
        for i, st in enumerate(data.segment_tracks):
            row = row + 1
            self._grid.attach(Gtk.Label.new(str(i + 1)), 0, row, 1, 1)
            self._grid.attach(self._build_box(st.time), 1, row, 1, 1)
            self._grid.attach(self._build_box(st.avgspeed), 2, row, 1, 1)
            self._grid.attach(self._build_box(st.maxspeed), 3, row, 1, 1)
            self._grid.attach(self._build_box(st.avghr), 4, row, 1, 1)
            self._grid.attach(self._build_box(st.maxhr), 5, row, 1, 1)
            self._grid.attach(self._build_box(st.avgcadence), 6, row, 1, 1)
            self._grid.attach(self._build_box(st.maxcadence), 7, row, 1, 1)
            self._grid.attach(self._build_activity_box(st.activity), 8, row, 1, 1)
            self._data_rows = self._data_rows + 1

        self._title_label.set_text(_("Segments"))

    def get_number_rows(self):
        return self._data_rows

    def _show_info_no_data(self):
        child = self.get_first_child()
        while child is not None:
            self.remove(child)
            child = self.get_first_child()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_start(50)
        box.set_margin_end(50)
        label1 = Gtk.Label.new(_("There are not anything to show"))
        label1.set_xalign(0.0)
        label2 = Gtk.Label.new(_(
            "Go to activity list, select one of them and create the segment you want clicking on the activity you can "
            "see on the map. You have to add two points on the map: start and end segment."
        ))
        label2.set_xalign(0.0)
        label1.get_style_context().add_class("pyot-h2")
        box.append(label1)
        box.append(label2)
        self.append(box)
        self.remove(self._top_box)

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

    def _build_activity_box(self, activity):
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)
        activity_name = Gtk.Label.new(activity.name)
        activity_name.set_xalign(0.0)
        activity_name.set_yalign(0.0)
        activity_name.set_wrap(True)
        activity_name.set_vexpand(True)
        vbox.append(activity_name)
        time_lbl = Gtk.Label.new(activity.stats.short_start_time)
        time_lbl.set_xalign(0.0)
        time_lbl.set_yalign(0.0)
        time_lbl.set_vexpand(True)
        vbox.append(time_lbl)
        return vbox

    def _build_box(self, value):
        """Builds a box with a label with value and styling."""
        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("pyot-stats-bg-color")
        box.set_homogeneous(False)
        label = Gtk.Label.new(value)
        label.set_xalign(0.0)
        label.set_yalign(0.0)
        label.set_vexpand(True)
        box.append(label)
        return box

    def _button_delete_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is None:
            MessageDialogError(
                transient_for=self._app.get_window(),
                text=_("There are not any segment selected"),
                title=_("Error deleting a segment")
            ).show()
            return

        def on_response(dialog, response):
            if response != Gtk.ResponseType.OK:
                dialog.close()
                return

            segmentid = self._segments_list_store[iter_item][0]
            DatabaseHelper.delete(DatabaseHelper.get_segment_by_id(segmentid))
            self._title_label.set_text(_("Loading segments..."))
            self._button_delete.set_sensitive(False)
            self._button_edit.set_sensitive(False)
            self._button_export.set_sensitive(False)
            self._segments_list_store.clear()

            self._on_data_ready(self._data_loading())

            dialog.close()

        dialog = QuestionDialog(
            parent=self._app.get_window(),
            title=_("Remove Segment"),
            question=_(f"Do you really want to remove the segment? This will remove all data about this segment.")
        )
        dialog.show()
        dialog.connect("response", on_response)

    def _button_edit_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is None:
            return

        def on_response(dialog, response):
            if response != Gtk.ResponseType.OK:
                dialog.close()
                return

            segment = dialog.get_segment()
            self._segments_list_store.set_value(iter_item, 1, segment.name)
            if self._label_segment_name:
                self._label_segment_name.set_label(segment.name)
            DatabaseHelper.update(segment)
            dialog.close()

        segmentid = self._segments_list_store[iter_item][0]
        dialog = SegmentEditDialog(parent=self._app.get_window(), segment=DatabaseHelper.get_segment_by_id(segmentid))
        dialog.show()
        dialog.connect("response", on_response)

    def _button_export_clicked_cb(self, btn):
        iter_item = self._combobox_segments.get_active_iter()
        if iter_item is None:
            return

        segment = DatabaseHelper.get_segment_by_id(self._segments_list_store[iter_item][0])
        fit_segment = FitSegment(segment).compute_binary()

        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                with open(SanitizeFile.fit_file(dialog.get_file().get_path()), "wb") as fd:
                    fd.write(fit_segment)

        dialog = ExportSegmentChooserDialog(
            parent=self._app.get_window(),
            on_response=on_response,
            current_name=SanitizeFile.fit_file(segment.name)
        )
        dialog.show()

