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
import threading

from gi.repository import Gtk, GLib

from pyopentracks.io.import_handler import ImportHandler
from pyopentracks.io.export_handler import ExportAllHandler
from pyopentracks.io.importer.importer import ImportResult
from pyopentracks.utils.utils import TypeActivityUtils as TAU
from pyopentracks.models.database_helper import DatabaseHelper


class PyotDialog(Gtk.Window):
    """General class to create modal windows (dialogs) for the app.

    This Gtk.Window contains a grid inside a scrolled window. This grid has
    4 columns. Child classes can create a dialog with some flexible features.
    """

    def __init__(self, parent: Gtk.Window):
        super().__init__()

        # Window configuration
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(600, 400)
        self.set_titlebar(Gtk.HeaderBar())

        # Child of the window: a scrolled window which contains a grid
        self._grid = Gtk.Grid()
        self._grid.set_margin_top(20)
        self._grid.set_margin_bottom(20)
        self._grid.set_margin_start(20)
        self._grid.set_margin_end(20)
        self._grid.set_column_spacing(5)
        self._grid.set_row_spacing(20)
        self._grid.set_halign(Gtk.Align.CENTER)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self._grid)

        self.set_child(scrolled_window)

    def with_size(self, w: int, h: int):
        self.set_default_size(w, h)
        return self

    def with_cancel_button(self, on_clicked_cb):
        button = Gtk.Button.new_with_label(_("Cancel"))
        button.connect("clicked", on_clicked_cb)
        self.get_titlebar().pack_start(button)
        return self

    def with_ok_button(self, on_clicked_cb):
        button = Gtk.Button.new_with_label(_("Ok"))
        button.connect("clicked", on_clicked_cb)
        self.get_titlebar().pack_end(button)
        return self

    def with_accept_button(self):
        button = Gtk.Button.new_with_label(_("Accept"))
        button.connect("clicked", lambda b: self.destroy())
        self.get_titlebar().pack_end(button)
        return self

    def with_title(self, title: str):
        """The title is set in the first row and it spans all 4 columns."""
        label = Gtk.Label.new(title)
        label.get_style_context().add_class("pyot-h3")
        label.set_wrap(True)
        label.set_margin_top(10)
        self._grid.attach(label, 0, 0, 4, 1)
        return self

    def with_text(self, text: str):
        """The text is set in the second row and it spans all 4 columns."""
        label = Gtk.Label.new(text)
        label.get_style_context().add_class("pyot-p-medium")
        label.set_wrap(True)
        label.set_xalign(0.0)
        self._grid.attach(label, 0, 1, 4, 1)
        return self

    def with_image_and_text(self, image_name: str, text: str):
        """
        The image is set in the first column of the second row and it spans 1 column.
        The text is set in the second column of the second row and it spans all 3 columns.
        """
        image = Gtk.Image.new_from_icon_name(image_name)
        label = Gtk.Label.new(text)
        label.set_wrap(True)
        label.set_xalign(0.0)
        label.get_style_context().add_class("pyot-p-medium")
        self._grid.attach(image, 0, 1, 1, 1)
        self._grid.attach(label, 1, 1, 3, 1)
        return self


class ImportExportResultDialog(Gtk.Window):
    def __init__(self, parent, folder, title, text_label, on_response_cb):
        super().__init__()

        # General properties
        self._on_response_cb = on_response_cb
        self._handler = None
        self._folder = folder

        self.connect("close-request", self._on_destroy)

        # Header bar with the Ok button
        header_bar = Gtk.HeaderBar()
        self._button = Gtk.Button.new_with_label(_("Ok"))
        self._button.connect("clicked", self._on_button_clicked)
        self._button.hide()
        header_bar.pack_start(self._button)

        # The title
        title_lbl = Gtk.Label.new(title)
        title_lbl.get_style_context().add_class("pyot-h3")
        title_lbl.set_margin_top(10)

        # The progress bar
        self._progress = Gtk.ProgressBar()

        # Message
        self._text_label = text_label
        self._label = Gtk.Label.new(f"{self._text_label}\n{self._folder}")
        self._label.set_margin_top(10)
        self._label.set_margin_bottom(10)
        self._label.set_margin_start(10)
        self._label.set_margin_end(10)
        self._label.get_style_context().add_class("pyot-p-medium")

        # List box where errors will be
        self._list_box = Gtk.ListBox()
        self._list_box.set_vexpand(True)
        self._list_box.hide()
        sw_with_list_box = Gtk.ScrolledWindow()
        sw_with_list_box.set_child(self._list_box)

        # Main box inside a scrolled window with all the contents
        scrolled_window = Gtk.ScrolledWindow()
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self._box.set_margin_top(20)
        self._box.set_margin_bottom(20)
        self._box.set_margin_start(20)
        self._box.set_margin_end(20)
        scrolled_window.set_child(self._box)

        self._box.append(title_lbl)
        self._box.append(self._progress)
        self._box.append(self._label)
        self._box.append(sw_with_list_box)

        # Properties of the window with the content
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(800, 600)
        self.set_titlebar(header_bar)
        self.set_child(scrolled_window)

        self._start()

    def _on_destroy(self, window):
        self._destroy_and_close()

    def _on_button_clicked(self, button):
        self._destroy_and_close()

    def _destroy_and_close(self):
        if self._handler:
            self._handler.stop()
        if self._on_response_cb:
            self._on_response_cb(Gtk.ResponseType.ACCEPT)
        self.destroy()

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


class AbstractEditDialog(Gtk.Window):
    def __init__(self, parent, on_ok_button_clicked_cb):
        super().__init__()

        # Window configuration
        self.set_title("PyOpenTracks")
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(600, 400)
        header_bar = Gtk.HeaderBar()
        self.set_titlebar(header_bar)

        # Child of the window: a scrolled widow which contains a grid
        self._grid = Gtk.Grid()
        self._grid.set_margin_top(20)
        self._grid.set_margin_bottom(20)
        self._grid.set_margin_start(20)
        self._grid.set_margin_end(20)
        self._grid.set_column_spacing(20)
        self._grid.set_row_spacing(20)
        self._grid.set_halign(Gtk.Align.CENTER)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self._grid)

        self.set_child(scrolled_window)

        # Other widgets
        self._type_list_store = Gtk.ListStore.new([str, str])

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", lambda b: self.destroy())

        ok_button = Gtk.Button.new_with_label(_("Ok"))
        ok_button.connect("clicked", on_ok_button_clicked_cb)

        header_bar.pack_start(cancel_button)
        header_bar.pack_end(ok_button)

        # Adds entries to the grid
        self._set_data()

    def _set_data(self):
        raise NotImplementedError()

    def get_object(self):
        raise NotImplementedError()


class ActivityEditDialog(AbstractEditDialog):
    """Activity's editor.

    This modal Gtk.Window can be used to edit a activity: name, description and
    activity type (category).

    It offers a method (get_object) to get the activity's changes.
    """
    def __init__(self, parent, activity, on_ok_button_clicked_cb):
        self._activity = activity
        super().__init__(parent, on_ok_button_clicked_cb)
        self.set_title("PyOpenTracks: Edit Activity")

    def _set_data(self):
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
        self._grid.attach(l1, 0, 0, 1, 1)
        self._grid.attach(name_entry, 1, 0, 1, 1)

        l2 = Gtk.Label.new(_("Description"))
        l2.set_xalign(0.0)
        self._grid.attach(l2, 0, 1, 1, 1)
        self._grid.attach(desc_entry, 1, 1, 1, 1)

        l3 = Gtk.Label.new(_("Category"))
        l3.set_xalign(0.0)
        self._grid.attach(l3, 0, 2, 1, 1)
        self._grid.attach(type_combo_box, 1, 2, 1, 1)

    def _on_name_changed(self, entry):
        self._activity.name = entry.get_text()

    def _on_description_changed(self, entry):
        self._activity.description = entry.get_text()

    def _on_activity_type_changed(self, combo):
        iter_item = combo.get_active_iter()
        if iter_item is not None:
            name, icon = self._type_list_store[iter_item][:2]
            self._activity.category = name

    def get_object(self):
        return self._activity


class SegmentEditDialog(AbstractEditDialog):
    """Segment's editor.

    It offers a method (get_object) to get the segment's changes.
    """

    def __init__(self, parent, segment, on_ok_button_clicked_cb):
        self._segment = segment
        super().__init__(parent, on_ok_button_clicked_cb)
        self.set_title("PyOpenTracks: Edit Segment")

    def _set_data(self):
        name = Gtk.Entry()
        name.set_text(self._segment.name)
        name.connect("changed", self._on_name_changed)

        label = Gtk.Label.new(_("Name"))
        label.set_xalign(0.0)

        self._grid.attach(label, 0, 0, 1, 1)
        self._grid.attach(name, 1, 0, 1, 1)

    def _on_name_changed(self, entry):
        self._segment.name = entry.get_text()

    def get_object(self):
        return self._segment

class ActivitiesRemoveDialog(Gtk.Window):
    """Modal Gtk.Window to remove a set of activities on background"""

    def __init__(self, parent, activities_ids, on_response_cb):
        super().__init__()

        # General properties
        self._on_response_cb = on_response_cb
        self._activities_ids = activities_ids

        self.connect("close-request", self._on_destroy)

        # Header bar with the Ok button
        header_bar = Gtk.HeaderBar()
        self._button = Gtk.Button.new_with_label(_("Ok"))
        self._button.connect("clicked", self._on_button_clicked)
        self._button.hide()
        header_bar.pack_start(self._button)

        # The title
        self._title_lbl = Gtk.Label.new(_("Removing activities..."))
        self._title_lbl.get_style_context().add_class("pyot-h3")
        self._title_lbl.set_margin_top(10)

        # The progress bar
        self._progress = Gtk.ProgressBar()

        # Message
        self._label = Gtk.Label.new(f"0 / {len(activities_ids)}")
        self._label.set_margin_top(10)
        self._label.set_margin_bottom(10)
        self._label.set_margin_start(10)
        self._label.set_margin_end(10)
        self._label.get_style_context().add_class("pyot-p-medium")

        # Main box inside a scrolled window with all the contents
        scrolled_window = Gtk.ScrolledWindow()
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self._box.set_margin_top(20)
        self._box.set_margin_bottom(20)
        self._box.set_margin_start(20)
        self._box.set_margin_end(20)
        scrolled_window.set_child(self._box)

        self._box.append(self._title_lbl)
        self._box.append(self._progress)
        self._box.append(self._label)

        # Properties of the window with the content
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(600, 400)
        self.set_titlebar(header_bar)
        self.set_child(scrolled_window)

    def show_and_run(self):
        self.show()
        threading.Thread(target=self._delete_in_thread, daemon=True).start()

    def _delete_in_thread(self):
        done = 0
        total = len(self._activities_ids)
        for id in self._activities_ids:
            try:
                activity = DatabaseHelper.get_activity_by_id(id)
                DatabaseHelper.delete(activity)
                done += 1
                self._label.set_text(f"{done} / {total}")
                self._progress.set_fraction(done/total)
            except ValueError:
                pyot_logging.get_logger(__name__).exception(
                    f"Error: deleting activity {id}"
                )
        GLib.idle_add(self._deletion_done)

    def _deletion_done(self):
        self._title_lbl.set_text(_(f"Activities deleted: {len(self._activities_ids)}"))
        self._button.show()

    def _on_destroy(self, window):
        self._on_response_cb(Gtk.ResponseType.ACCEPT)
        self.destroy()

    def _on_button_clicked(self, button):
        self._on_response_cb(Gtk.ResponseType.ACCEPT)
        self.destroy()

