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

from pyopentracks.io.import_handler import ImportHandler
from pyopentracks.io.export_handler import ExportAllHandler
from pyopentracks.io.importer.importer import ImportResult
from pyopentracks.utils.utils import TypeActivityUtils as TAU


class QuestionDialog(Gtk.Dialog):

    def __init__(self, parent, title, question):
        Gtk.Dialog.__init__(
            self,
            title=title,
            transient_for=parent
        )
        btn1 = self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        btn1.set_margin_start(10)
        btn1.set_margin_end(10)
        btn1.set_margin_top(10)
        btn1.set_margin_bottom(20)
        btn2 = self.add_button(_("Ok"), Gtk.ResponseType.OK)
        btn2.set_margin_end(20)
        btn2.set_margin_top(10)
        btn2.set_margin_bottom(20)

        self.set_default_size(150, 100)

        label = Gtk.Label(label=question)

        box = self.get_content_area()
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.append(label)


class MessageDialogError(Gtk.MessageDialog):

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK
        )
        image = Gtk.Image()
        image.set_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)
        image.show()
        self.set_image(image)

    def show(self):
        self.run()
        self.destroy()


class ImportExportResultDialog(Gtk.Dialog):
    def __init__(self, parent, folder, title, text_label, on_response_cb):
        Gtk.Dialog.__init__(
            self,
            title=title,
            transient_for=parent
        )
        self._on_response_cb = on_response_cb
        self._handler = None
        self._folder = folder
        self._box = self.get_content_area()
        self._progress = Gtk.ProgressBar()
        self._label = None
        self._text_label = text_label
        self._list_box = None
        self._button = self.add_button(_("Ok"), Gtk.ResponseType.ACCEPT)
        self._setup_ui()
        self._start()

    def _on_destroy(self, widget, data):
        if self._handler:
            self._handler.stop()

    def _setup_ui(self):
        self._label = Gtk.Label(
            label=f"{self._text_label}\n{self._folder}"
        )
        self._label.set_margin_top(10)
        self._label.set_margin_bottom(10)
        self._label.set_margin_start(10)
        self._label.set_margin_end(10)
        self._label.get_style_context().add_class("pyot-p-medium")

        self._button.set_margin_top(10)
        self._button.set_margin_bottom(10)
        self._button.set_margin_start(10)
        self._button.set_margin_end(10)

        scrolled_window = Gtk.ScrolledWindow()
        self._list_box = Gtk.ListBox()
        scrolled_window.set_child(self._list_box)

        self._box.append(self._progress)
        self._box.append(self._label)
        self._box.append(scrolled_window)

        self.connect("response", self._on_response)

        self.set_default_size(400, 300)

        self._list_box.hide()
        self._button.hide()

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.close()
        if self._on_response_cb:
            self._on_response_cb(dialog, response)

    def _start(self):
        raise NotImplementedError("ImportExportResultDialog._start not implemented")


class ImportResultDialog(ImportExportResultDialog):

    def __init__(self, parent, filename, on_response_cb):
        super().__init__(parent, filename, _("Importing..."), _("Importing files:"), on_response_cb)

    def _start(self):
        self._progress.set_fraction(0)
        self._handler = ImportHandler()
        self._handler.connect("total-files-to-import", self._total_files_cb)
        self._handler.import_folder(self._folder, self._import_ended_cb)

    def _total_files_cb(self, handler: ImportHandler, total_files):
        self._label.set_text(f"0 / {total_files}")

    def _import_ended_cb(self, result: ImportResult):
        self._progress.set_fraction(result.total_imported / result.total)
        if not result.is_done:
            self._label.set_text(f"{result.total_imported} / {result.total}")
            return

        self._label.set_text(_(f"Total imported: {result.imported}"))
        if result.is_error:
            self._label.set_text(
                self._label.get_text() + ".\n" +
                _("Finished with errors") + ":"
            )
            for e in result.errors:
                row = Gtk.ListBoxRow()
                label = Gtk.Label(label=e, xalign=0.0)
                row.set_child(label)
                self._list_box.append(row)
            self._list_box.show()
        self._button.show()


class ExportResultDialog(ImportExportResultDialog):
    def __init__(self, parent, folder, on_response_cb=None):
        self._total = 0
        self._exported = 0
        self._errors = []
        super().__init__(parent, folder, _("Exporting..."), _("Exporting files to folder:"), on_response_cb)

    def _start(self):
        handler = ExportAllHandler(self._folder, self._export_all_ended)
        handler.run()
        handler.connect("total-activities-to-export", self._total_activities_cb)

    def _total_activities_cb(self, handler: ExportAllHandler, total_activities):
        self._total = total_activities
        self._label.set_text(f"{self._exported} / {self._total}")

    def _export_all_ended(self, result):
        if not result.is_ok:
            self._errors.append({
                "activity_name": result.filename,
                "message": result.message
            })

        self._exported = self._exported + 1
        self._progress.set_fraction(self._exported / self._total)
        if not self._exported == self._total:
            self._label.set_text(f"{self._exported} / {self._total}")
            return

        self._label.set_text(_(f"Total exported: {self._exported}"))
        if len(self._errors) > 0:
            self._label.set_text(
                self._label.get_text() + ".\n" +
                _("Finished with errors") + ":"
            )
            for e in self._errors:
                row = Gtk.ListBoxRow()
                activity_name = e["activity_name"]
                message = e["message"]
                label = Gtk.Label.new(f"{activity_name}: {message}")
                label.set_xalign(0.0)
                row.set_child(label)
                self._list_box.append(row)
            self._list_box.show()
        self._button.show()


class ActivityEditDialog(Gtk.Dialog):
    """Activity's dialog editor.

    This dialog can be used to edit a activity: name, description and
    activity type (category).

    It offers a method (get_activity) to get the activity's changes.
    """

    def __init__(self, parent, activity):
        Gtk.Dialog.__init__(
            self,
            title=_("Edit Activity"),
            transient_for=parent
        )
        self._activity = activity
        self._type_list_store = Gtk.ListStore.new([str, str])
        self._box = self.get_content_area()
        btn1 = self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        btn1.set_margin_start(10)
        btn1.set_margin_end(10)
        btn1.set_margin_top(10)
        btn1.set_margin_bottom(20)
        btn2 = self.add_button(_("Ok"), Gtk.ResponseType.OK)
        btn2.set_margin_end(20)
        btn2.set_margin_top(10)
        btn2.set_margin_bottom(20)
        self._set_data()

    def _set_data(self):
        grid = Gtk.Grid()
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        name_entry = Gtk.Entry()
        name_entry.set_text(self._activity.name)
        name_entry.connect("changed", self._on_name_changed)

        desc_entry = Gtk.Entry()
        desc_entry.set_text(self._activity.description)
        desc_entry.connect("changed", self._on_description_changed)

        type_combo_box = Gtk.ComboBox.new_with_model(self._type_list_store)
        renderer_text = Gtk.CellRendererText()
        type_combo_box.pack_start(renderer_text, True)
        type_combo_box.add_attribute(renderer_text, "text", 0)
        for idx, item in enumerate(TAU.get_activity_types()):
            self._type_list_store.append(item)
            if item[0] == self._activity.category:
                type_combo_box.set_active(idx)
        type_combo_box.connect("changed", self._on_activity_type_changed)

        l1 = Gtk.Label.new(_("Name"))
        l1.set_xalign(0.0)
        grid.attach(l1, 0, 0, 1, 1)
        grid.attach(name_entry, 1, 0, 1, 1)

        l2 = Gtk.Label.new(_("Description"))
        l2.set_xalign(0.0)
        grid.attach(l2, 0, 1, 1, 1)
        grid.attach(desc_entry, 1, 1, 1, 1)

        l3 = Gtk.Label.new(_("Category"))
        l3.set_xalign(0.0)
        grid.attach(l3, 0, 2, 1, 1)
        grid.attach(type_combo_box, 1, 2, 1, 1)

        self._box.append(grid)

    def _on_name_changed(self, entry):
        self._activity.name = entry.get_text()

    def _on_description_changed(self, entry):
        self._activity.description = entry.get_text()

    def _on_activity_type_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            name, icon = self._type_list_store[iter_item][:2]
            self._activity.category = name

    def get_activity(self):
        return self._activity


class SegmentEditDialog(Gtk.Dialog):
    """Segment's dialog editor.

    It offers a method (get_segment) to get the segment's changes.
    """

    def __init__(self, parent, segment):
        Gtk.Dialog.__init__(
            self,
            title=_("Edit Segment"),
            transient_for=parent
        )
        self._segment = segment
        self._box = self.get_content_area()
        btn1 = self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        btn1.set_margin_start(10)
        btn1.set_margin_end(10)
        btn1.set_margin_top(10)
        btn1.set_margin_bottom(20)
        btn2 = self.add_button(_("Ok"), Gtk.ResponseType.OK)
        btn2.set_margin_end(20)
        btn2.set_margin_top(10)
        btn2.set_margin_bottom(20)
        self._set_data()

    def _set_data(self):
        grid = Gtk.Grid()
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        name = Gtk.Entry()
        name.set_text(self._segment.name)
        name.connect("changed", self._on_name_changed)

        label = Gtk.Label.new(_("Name"))
        label.set_xalign(0.0)

        grid.attach(label, 0, 0, 1, 1)
        grid.attach(name, 1, 0, 1, 1)

        self._box.append(grid)

    def _on_name_changed(self, entry):
        self._segment.name = entry.get_text()

    def get_segment(self):
        return self._segment

