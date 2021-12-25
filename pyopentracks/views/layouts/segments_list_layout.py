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

from pyopentracks.views.dialogs import QuestionDialog, MessageDialogError, SegmentEditDialog
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.maps.base_map import BaseMap


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segments_list_layout.ui")
class SegmentsListLayout(Gtk.Box):
    __gtype_name__ = "SegmentsListLayout"

    _box_header: Gtk.Box = Gtk.Template.Child()
    _title_label: Gtk.Label = Gtk.Template.Child()
    _combobox_segments: Gtk.ComboBox = Gtk.Template.Child()
    _button_delete: Gtk.Button = Gtk.Template.Child()
    _button_edit: Gtk.Button = Gtk.Template.Child()
    _segments_list_store: Gtk.ListStore = Gtk.Template.Child()
    _grid_segment_detail: Gtk.Grid = Gtk.Template.Child()
    _grid: Gtk.Grid = Gtk.Template.Child()

    class Data:
        def __init__(self, segment, segmentracks):
            self.segment = segment
            self.segment_tracks = []
            for st in segmentracks:
                self.segment_tracks.append({
                    "segmentrack_object": st,
                    "track_object": DatabaseHelper.get_track_by_id(st.trackid)
                })

    def __init__(self):
        super().__init__()

        self._data_rows = 0
        self._map = None

        self._button_delete.connect("clicked", self._button_delete_clicked_cb)
        self._button_edit.connect("clicked", self._button_edit_clicked_cb)

        self._button_delete.set_sensitive(False)
        self._button_edit.set_sensitive(False)

        self._label_segment_name = None

        self._title_label.set_text(_("Segments"))
        self._title_label.set_line_wrap(True)
        self._title_label.set_margin_top(20)
        self._title_label.set_margin_left(20)
        self._title_label.get_style_context().add_class("pyot-h2")

        self._grid_segment_detail.get_style_context().add_class("pyot-stats-bg-color")

        self.get_style_context().add_class("pyot-bg")

    @staticmethod
    def from_trackid(trackid):
        object = SegmentsListLayout()
        object._combobox_segments.hide()
        object.remove(object._grid_segment_detail)
        object._box_header.remove(object._button_edit)
        object._box_header.remove(object._button_delete)
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
        object._title_label.set_text(_("Loading segments..."))
        ProcessView(object._on_data_ready, object._data_loading, None).start()
        return object

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

        return SegmentsListLayout.Data(segments[0], DatabaseHelper.get_segment_tracks_by_segmentid(segments[0].id))

    def _data_changing(self, segmentid):
        segment = DatabaseHelper.get_segment_by_id(segmentid)
        return SegmentsListLayout.Data(segment, DatabaseHelper.get_segment_tracks_by_segmentid(segment.id))

    def _on_data_ready(self, data: Data):
        for w in self._grid.get_children():
            self._grid.remove(w)
        for w in self._grid_segment_detail.get_children():
            self._grid_segment_detail.remove(w)

        if not data:
            self._show_info_no_data()
            return

        self._button_delete.set_sensitive(True)
        self._button_edit.set_sensitive(True)

        segment = data.segment
        segment_tracks = data.segment_tracks

        self._grid_segment_detail.attach(
            self._build_header_label(_("Name:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 0, 1, 1
        )
        self._label_segment_name = self._build_header_label(
            segment.name, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20
        )
        self._grid_segment_detail.attach(self._label_segment_name, 1, 0, 1, 1)
        self._grid_segment_detail.attach(
            self._build_header_label(_("Distance:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 1, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(segment.distance, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 1, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(_("Elevation Gain:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 2, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(segment.gain, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 2, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(_("Elevation Loss:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 3, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(segment.loss, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 3, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(_("Slope:"), xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            0, 4, 1, 1
        )
        self._grid_segment_detail.attach(
            self._build_header_label(segment.slope, xalign=0.0, margin_top=20, margin_bottom=10, margin_left=20),
            1, 4, 1, 1
        )

        self._map = BaseMap()
        self._map.add_polyline([(sp.latitude, sp.longitude) for sp in DatabaseHelper.get_segment_points(segment.id)])
        self._grid_segment_detail.attach(self._map, 2, 0, 4, 5)

        top = 0

        self._grid.attach(Gtk.Label(_("Time")), 0, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Speed")), 1, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Speed")), 2, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Heart Rate")), 3, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Heart Rate")), 4, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Avg. Cadence")), 5, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Max. Cadence")), 6, top, 1, 1)
        self._grid.attach(Gtk.Label(_("Activity Information")), 7, top, 1, 1)
        for i in segment_tracks:
            st = i["segmentrack_object"]
            top = top + 1
            self._grid.attach(self._build_box(st.time), 0, top, 1, 1)
            self._grid.attach(self._build_box(st.avgspeed), 1, top, 1, 1)
            self._grid.attach(self._build_box(st.maxspeed), 2, top, 1, 1)
            self._grid.attach(self._build_box(st.avghr), 3, top, 1, 1)
            self._grid.attach(self._build_box(st.maxhr), 4, top, 1, 1)
            self._grid.attach(self._build_box(st.avgcadence), 5, top, 1, 1)
            self._grid.attach(self._build_box(st.maxcadence), 6, top, 1, 1)
            self._grid.attach(self._build_track_box(i["track_object"]), 7, top, 1, 1)
            self._data_rows = self._data_rows + 1

        self._title_label.set_text(_("Segments"))
        self.show_all()

    def get_number_rows(self):
        return self._data_rows

    def _show_info_no_data(self):
        box = Gtk.VBox(margin=20)
        label1 = Gtk.Label(_("There are not anything to show"), xalign=0.0)
        label2 = Gtk.Label(_(
            "Go to track list, select one of them and create the segment you want clicking on the track you can "
            "see on the map. You have to add two points on the map: start and end segment."
        ))
        label1.get_style_context().add_class("pyot-h2")
        box.pack_start(label1, True, True, 10)
        box.pack_start(label2, True, True, 10)
        self._grid.attach(box, 0, 0, 1, 1)
        self._title_label.set_text(_("Segments"))
        self.remove(self._box_header)
        self.remove(self._grid_segment_detail)
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
        self._segments_list_store.clear()

        self._on_data_ready(self._data_loading())
        #ProcessView(self._on_data_ready, self._data_loading, None).start()

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
