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

from gi.repository import Gtk, GLib, GdkPixbuf
from pyopentracks.app_activity_analytic import AppActivityAnalytic

from pyopentracks.app_interfaces import ActionId
from pyopentracks.app_activity_list_interfaces import ActionsTuple
from pyopentracks.utils import logging as pyot_logging
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.activity_stats_layout import ActivityStatsLayout
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.dialogs import QuestionDialog, ActivityEditDialog
from pyopentracks.utils.utils import TypeActivityUtils
from pyopentracks.views.layouts.process_view import QueuedProcessesView
from pyopentracks.tasks.altitude_correction import AltitudeCorrection


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/activities_layout.ui")
class ActivitiesLayout(Gtk.Paned, Layout):
    __gtype_name__ = "ActivitiesLayout"

    _tree_view_widget: Gtk.TreeView = Gtk.Template.Child()
    _activity_stats_widget: Gtk.ScrolledWindow = Gtk.Template.Child()
    _entry_search_widget: Gtk.Entry = Gtk.Template.Child()

    def __init__(self, app, activities):
        """Init function for the list of activities.

        Arguments:
        app        -- AppActivityList instance.
        activities -- list of Activity's object.
        """
        super().__init__()
        Layout.__init__(self)

        self._app = app
        self._treepath_selected = None

        self._show_message(_("Select an activity to view its stats..."))

        self._activities = activities
        self._list_store = Gtk.ListStore(int, str, GdkPixbuf.Pixbuf)
        for activity in self._activities:
            self._list_store.append([
                activity.id,
                activity.name,
                TypeActivityUtils.get_icon_pixbuf(activity.category, 32, 32)
            ])

        self._current_model_filter = None
        self._tree_model_filter = self._list_store.filter_new()
        self._tree_model_filter.set_visible_func(self._on_list_store_filter_func)

        self._tree_view_widget.set_model(self._tree_model_filter)
        self._tree_view_widget.append_column(
            Gtk.TreeViewColumn(cell_renderer=Gtk.CellRendererPixbuf(), pixbuf=2)
        )
        self._tree_view_widget.append_column(
            Gtk.TreeViewColumn(_("Activities"), Gtk.CellRendererText(), text=1)
        )
        self._list_store.connect("row-deleted", self._on_list_store_row_deleted)

        self._tree_selection = self._tree_view_widget.get_selection()
        self._tree_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self._tree_selection.connect("changed", self._on_tree_selection_changed)

        self._select_first_row()

        self._entry_search_widget.set_placeholder_text(_("Search Activities"))
        self._entry_search_widget.connect("activate", self._on_search_text_changed)
        self._entry_search_widget.connect("icon-press", self._on_search_text_icon_pressed)

    def build(self):
        self.show_all()

    def on_remove_bulk(self, widget, treeiter_list):
        dialog = QuestionDialog(
            parent=self._app.get_window(),
            title=_("Remove Activities"),
            question=_(f"Do you really want to remove all selected activities")
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.CANCEL:
            return

        def deletion_done():
            childiters = [
                self._tree_model_filter.convert_iter_to_child_iter(treeiter)
                for treeiter in treeiter_list
            ]
            for childiter in childiters:
                self._list_store.remove(childiter)
            self._treepath_selected = None
            self._tree_view_widget.set_sensitive(True)
            self._select_first_row()

        def delete_in_thread():
            total = len(treeiter_list)
            done = 0
            for treeiter in treeiter_list:
                self._remove_item_from_db(treeiter)
                done = done + 1
                self._app.get_window().loading(done / total)
            GLib.idle_add(deletion_done)

        self._tree_view_widget.set_sensitive(False)
        threading.Thread(target=delete_in_thread, daemon=True).start()

    def on_remove(self, widget, treeiter):
        """Callback to remove the treeiter item from list store.

        Remove from the model (Gtk.ListStore) the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        activity_name = self._tree_model_filter.get_value(treeiter, 1)
        dialog = QuestionDialog(
            parent=self._app.get_window(),
            title=_("Remove Activity"),
            question=_(f"Do you really want to remove activity {activity_name}")
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.CANCEL:
            return
        self._remove_item_from_db(treeiter)
        self._remove_item_from_list_store(treeiter)

    def on_edit(self, widget, treeiter):
        """Callback to edit the treeiter item from list store.

        Edit from the model (Gtk.ListStore) the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        activity_id = self._tree_model_filter.get_value(treeiter, 0)

        activity = DatabaseHelper.get_activity_by_id(activity_id)
        dialog = ActivityEditDialog(parent=self._app.get_window(), activity=activity)
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return

        activity = dialog.get_activity()
        self._tree_model_filter.set_value(treeiter, 1, activity.name)
        self._tree_model_filter.set_value(
            treeiter, 2, TypeActivityUtils.get_icon_pixbuf(activity.category, 32, 32)
        )
        DatabaseHelper.update(activity)

        funcs = []
        if dialog.correct_altitude():
            altitude_correction = AltitudeCorrection(activity.id)
            funcs.append({"func": altitude_correction.run, "args": None})

        if funcs:
            self._app.get_window().show_infobar(
                itype=Gtk.MessageType.INFO,
                message=_(
                    "Doing corrections. When it finishes then the activity will "
                    "be reloaded"
                ),
                buttons=[
                    {
                     "text": _("Ok"),
                     "cb": lambda b: self._app.get_window().clean_top_widget()
                    }
                ]
            )
            QueuedProcessesView(self._on_correction_done, funcs).start()
        else:
            self._select_row(self._tree_model_filter.get_path(treeiter), force=True)

    def on_analytic(self, widget, treeiter):
        """Callback to open analytic for the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        activity = DatabaseHelper.get_activity_by_id(self._tree_model_filter.get_value(treeiter, 0))
        self._app.open_external_app(AppActivityAnalytic, {"activity": activity})
        # self._app_window.load_app(AppAnalytic(activity))

    def _on_correction_done(self, results):
        if results is None:
            self._app.get_window().clean_top_widget()
            self._app.get_window().show_infobar(
                itype=Gtk.MessageType.ERROR,
                message=_(
                    "An error was triggered and correction wasn't done."
                ),
                buttons=[
                    {
                        "text": _("Ok"),
                        "cb": lambda b: self._app.get_window().clean_top_widget()
                    }
                ]
            )
            return

        activity = results[0]
        self._app.get_window().clean_top_widget()
        iter = self._tree_model_filter.get_iter_first()
        while iter and self._tree_model_filter.get_value(iter, 0) != activity.id:
            iter = self._tree_model_filter.iter_next(iter)
        if self._treepath_selected == self._tree_model_filter.get_path(iter):
            self._select_row(self._tree_model_filter.get_path(iter), force=True)

    def _select_first_row(self):
        if len(self._tree_model_filter) > 0:
            self._select_row(Gtk.TreePath.new_from_string("0"), True)
        else:
            self._app.register_actions([])
            self._show_message(_("There are not results for the selected filters"))

    def _select_row(self, treepath, force=False):
        """It loads treepath item.

        It only loads the treepath item if it's a different currently load one.

        Also, if force == True, then it forces the treepath loading.
        """
        if self._treepath_selected == treepath and not force:
            return
        self._treepath_selected = treepath

        treeiter = self._tree_model_filter.get_iter(treepath)
        activity_id = self._tree_model_filter.get_value(treeiter, 0)
        activity = DatabaseHelper.get_activity_by_id(activity_id)
        if not activity:
            return

        self._tree_view_widget.set_cursor(treepath, None, False)
        self._tree_view_widget.grab_focus()

        layout = ActivityStatsLayout(activity)
        self._add_widget(layout)
        layout.build()

        self._app.register_actions([
            ActionsTuple(ActionId.DELETE, self.on_remove, treeiter),
            ActionsTuple(ActionId.EDIT, self.on_edit, treeiter),
            ActionsTuple(ActionId.DETAIL, self.on_analytic, treeiter),
        ])

    def _show_message(self, msg):
        label = Gtk.Label(label=msg)
        label.get_style_context().add_class("pyot-h1")
        self._add_widget(label)

    def _add_widget(self, widget):
        """Add the widget to _activity_stats_widget.

        Arguments:
        widget -- the widget to add to ScrolledWindow _activity_stats_widget.
        """
        if self._activity_stats_widget and self._activity_stats_widget.get_child():
            self._activity_stats_widget.remove(
                self._activity_stats_widget.get_child()
            )
        self._activity_stats_widget.add(widget)
        self.show_all()

    def _remove_item_from_db(self, treeiter):
        """Remove from the model the item pointed by treeiter

        Arguments
        treeiter -- Gtk.TreeIter object that point to the item to be deleted from the model.
        """
        try:
            activity_id = self._tree_model_filter.get_value(treeiter, 0)
            activity = DatabaseHelper.get_activity_by_id(activity_id)
            DatabaseHelper.delete(activity)
        except ValueError:
            pyot_logging.get_logger(__name__).exception(
                f"Error: deleting activity {self._tree_model_filter.get_value(treeiter, 1)}"
            )

    def _remove_item_from_list_store(self, treeiter):
        """Remove from Gtk.ListStore the item pointed by treeiter.

        Arguments
        treeiter -- Gtk.TreeIter object that point to the item to be deleted from Gtk.ListStore.
        """
        self._treepath_selected = None
        childiter = self._tree_model_filter.convert_iter_to_child_iter(treeiter)
        self._list_store.remove(childiter)

    def _on_tree_selection_changed(self, selection):
        model, treepath_list = selection.get_selected_rows()
        if len(treepath_list) == 1:
            self._select_row(treepath_list[0])
            self._app.register_actions([
                ActionsTuple(ActionId.DELETE, self.on_remove, self._tree_model_filter.get_iter(treepath_list[0])),
                ActionsTuple(ActionId.EDIT, self.on_edit, self._tree_model_filter.get_iter(treepath_list[0])),
                ActionsTuple(ActionId.DETAIL, self.on_analytic, self._tree_model_filter.get_iter(treepath_list[0])),
            ])
        else:
            self._app.register_actions([
                ActionsTuple(
                    ActionId.DELETE,
                    self.on_remove_bulk,
                    tuple([self._tree_model_filter.get_iter(treepath) for treepath in treepath_list])
                )
            ])

    def _on_list_store_row_deleted(self, treemodel, treepath):
        if len(self._list_store) == 0:
            self._app.empty()
        if len(self._tree_model_filter) == 0:
            self._app.register_actions([])
            self._show_message(_("Select a activity to view its stats..."))

    def _on_list_store_filter_func(self, treemodel, treeiter, data):
        if self._current_model_filter is None:
            return True
        else:
            return len(
                list(
                    filter(
                        lambda i: i.lower() in treemodel[treeiter][1].lower(),
                        self._current_model_filter.split()
                    )
                )
            ) > 0

    def _on_search_text_changed(self, entry):
        self._current_model_filter = entry.get_text().strip() if entry.get_text().strip() else None
        self._tree_model_filter.refilter()
        self._select_first_row()

    def _on_search_text_icon_pressed(self, entry, position, event):
        if position == Gtk.EntryIconPosition.PRIMARY:
            self._on_search_text_changed(entry)
        else:
            self._entry_search_widget.set_text("")
            self._current_model_filter = None
            self._tree_model_filter.refilter()
            self._select_first_row()
