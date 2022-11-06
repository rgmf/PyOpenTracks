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
            transient_for=parent,
            flags=0
        )
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(150, 100)

        label = Gtk.Label(label=question)

        box = self.get_content_area()
        box.add(label)
        self.show_all()


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
    def __init__(self, parent, folder, title, text_label):
        Gtk.Dialog.__init__(
            self,
            title=title,
            transient_for=parent,
            flags=0
        )
        self._handler = None
        self._folder = folder
        self._box = self.get_content_area()
        self._progress = Gtk.ProgressBar()
        self._label = None
        self._text_label = text_label
        self._list_box = None
        self._setup_ui()
        self._start()
        self.connect("delete-event", self._on_destroy)

    def _on_destroy(self, widget, data):
        if self._handler:
            self._handler.stop()

    def _setup_ui(self):
        self._label = Gtk.Label(
            label=f"{self._text_label}\n{self._folder}"
        )
        self._label.get_style_context().add_class("pyot-p-medium")

        scrolled_window = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        self._list_box = Gtk.ListBox()

        viewport.add(self._list_box)
        scrolled_window.add(viewport)

        self._box.pack_start(self._progress, False, False, 0)
        self._box.pack_start(self._label, True, True, 0)
        self._box.pack_start(scrolled_window, True, True, 0)

        self.set_default_size(400, 300)

        self.show_all()
        self._list_box.hide()

    def _start(self):
        raise NotImplementedError("ImportExportResultDialgo._start not implemented")


class ImportResultDialog(ImportExportResultDialog):

    def __init__(self, parent, filename):
        super().__init__(parent, filename, _("Importing..."), _("Importing files:"))

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
                row.add(label)
                self._list_box.add(row)
            self._list_box.show_all()

        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)


class ExportResultDialog(ImportExportResultDialog):
    def __init__(self, parent, folder):
        self._total = 0
        self._exported = 0
        self._errors = []
        super().__init__(parent, folder, _("Exporting..."), _("Exporting files to folder:"))

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
                label = Gtk.Label(label=f"{activity_name}: {message}", xalign=0.0)
                row.add(label)
                self._list_box.add(row)
            self._list_box.show_all()
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/activity_edit_dialog.ui")
class ActivityEditDialog(Gtk.Dialog):
    """Activity's dialog editor.

    This dialog can be used to edit a activity: name, description and
    activity type (category).

    It offers a method (get_activity) to get the activity's changes.
    """

    __gtype_name__ = "ActivityEditDialog"

    _name: Gtk.Entry = Gtk.Template.Child()
    _description: Gtk.Entry = Gtk.Template.Child()
    _activity_type: Gtk.ComboBox = Gtk.Template.Child()
    _type_list_store: Gtk.ListStore = Gtk.Template.Child()
    _altitude_correction: Gtk.CheckButton = Gtk.Template.Child()

    def __init__(self, parent, activity):
        Gtk.Dialog.__init__(
            self,
            title=_("Edit Activity"),
            transient_for=parent,
            flags=0
        )
        self._activity = activity
        self._set_data()
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.show_all()

    def _set_data(self):
        self._name.set_text(self._activity.name)
        self._name.connect("changed", self._on_name_changed)

        self._description.set_text(self._activity.description)
        self._description.connect("changed", self._on_description_changed)

        for idx, item in enumerate(TAU.get_activity_types()):
            self._type_list_store.append(item)
            if item[0] == self._activity.category:
                self._activity_type_name = item[0]
                self._activity_type.set_active(idx)
        self._activity_type.connect("changed", self._on_activity_type_changed)

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

    def correct_altitude(self):
        return self._altitude_correction.get_active()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/segment_edit_dialog.ui")
class SegmentEditDialog(Gtk.Dialog):
    """Segment's dialog editor.

    It offers a method (get_segment) to get the segment's changes.
    """

    __gtype_name__ = "SegmentEditDialog"

    _name: Gtk.Entry = Gtk.Template.Child()

    def __init__(self, parent, segment):
        Gtk.Dialog.__init__(
            self,
            title=_("Edit Segment"),
            transient_for=parent,
            flags=0
        )
        self._segment = segment
        self._set_data()
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.show_all()

    def _set_data(self):
        self._name.set_text(self._segment.name)
        self._name.connect("changed", self._on_name_changed)

    def _on_name_changed(self, entry):
        self._segment.name = entry.get_text()

    def get_segment(self):
        return self._segment
