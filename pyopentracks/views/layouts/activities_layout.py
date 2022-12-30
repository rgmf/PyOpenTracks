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
from gi.repository import Gtk, GLib, GdkPixbuf
from pyopentracks.app_activity_analytic import AppActivityAnalytic

from pyopentracks.app_interfaces import ActionId
from pyopentracks.app_activity_list_interfaces import ActionsTuple
from pyopentracks.utils import logging as pyot_logging
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.activity_stats_layout import ActivityStatsLayout
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.dialogs import (
    PyotDialog, ActivityEditDialog, ActivitiesRemoveDialog
)
from pyopentracks.utils.utils import TypeActivityUtils
from pyopentracks.views.layouts.process_view import QueuedProcessesView
from pyopentracks.tasks.altitude_correction import AltitudeCorrection


class ActivitiesLayout(Gtk.Paned, Layout):

    def __init__(self, app, activities):
        """Init function for the list of activities.

        Arguments:
        app        -- AppActivityList instance.
        activities -- list of Activity's object.
        """
        super().__init__()
        Layout.__init__(self)

        self._box_with_tree = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._box_with_tree.set_size_request(300, -1)
        self._entry_search_widget = Gtk.Entry()
        scrolled_window_for_tree = Gtk.ScrolledWindow()
        scrolled_window_for_tree.set_vexpand(True)
        self._tree_view_widget = Gtk.TreeView()
        scrolled_window_for_tree.set_child(self._tree_view_widget)
        self._box_with_tree.append(self._entry_search_widget)
        self._box_with_tree.append(scrolled_window_for_tree)
        self._activity_stats_widget = Gtk.ScrolledWindow()

        self.set_start_child(self._box_with_tree)
        self.set_resize_start_child(False)
        self.set_shrink_start_child(False)

        self.set_end_child(self._activity_stats_widget)
        self.set_resize_end_child(True)
        self.set_shrink_end_child(False)

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
        pass

    def on_remove_bulk(self, widget, treeiter_list):
        dialog = PyotDialog(self._app.get_window())

        def on_cancel(button):
            dialog.destroy()

        def on_ok(button):
            dialog.destroy()
            def deletion_done(response):
                childiters = [
                    self._tree_model_filter.convert_iter_to_child_iter(treeiter)
                    for treeiter in treeiter_list
                ]
                for childiter in childiters:
                    self._list_store.remove(childiter)
                self._treepath_selected = None
                self._tree_view_widget.set_sensitive(True)
                self._select_first_row()

            activities_ids = [
                self._tree_model_filter.get_value(treeiter, 0) for treeiter in treeiter_list
            ]
            removeDialog = ActivitiesRemoveDialog(self._app.get_window(), activities_ids, on_response_cb=deletion_done)
            removeDialog.show_and_run()

        dialog.with_title(_("Remove Activities"))\
            .with_image_and_text("question-round-symbolic", _(f"Do you really want to remove all selected activities?"))\
            .with_cancel_button(on_cancel)\
            .with_ok_button(on_ok)\
            .show()

    def on_remove(self, widget, treeiter):
        """Callback to remove the treeiter item from list store.

        Remove from the model (Gtk.ListStore) the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        dialog = PyotDialog(self._app.get_window())

        def on_cancel(button):
            dialog.destroy()

        def on_ok(button):
            self._remove_item_from_db(treeiter)
            self._remove_item_from_list_store(treeiter)
            dialog.destroy()

        activity_name = self._tree_model_filter.get_value(treeiter, 1)
        dialog.with_title(_("Remove Activity"))\
            .with_image_and_text("question-round-symbolic", _(f"Do you really want to remove activity {activity_name}?"))\
            .with_cancel_button(on_cancel)\
            .with_ok_button(on_ok)\
            .show()

    def on_edit(self, widget, treeiter):
        """Callback to edit the treeiter item from list store.

        Edit from the model (Gtk.ListStore) the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        def on_ok_button_clicked(button):
            activity = dialog.get_object()
            self._tree_model_filter.set_value(treeiter, 1, activity.name)
            self._tree_model_filter.set_value(
                treeiter, 2, TypeActivityUtils.get_icon_pixbuf(activity.category, 32, 32)
            )
            DatabaseHelper.update(activity)
            self._select_row(self._tree_model_filter.get_path(treeiter), force=True)
            dialog.close()

        activity_id = self._tree_model_filter.get_value(treeiter, 0)

        activity = DatabaseHelper.get_activity_by_id(activity_id)
        dialog = ActivityEditDialog(self._app.get_window(), activity, on_ok_button_clicked)
        dialog.show()

    def on_analytic(self, widget, treeiter):
        """Callback to open analytic for the treeiter item.

        Arguments:
        widget   -- the Gtk.Widget that trigger this callback.
        treeiter -- the Gtk.TreeIter that can be used to access to the node in
                    the Gtk.TreeView through the model.
        """
        activity = DatabaseHelper.get_activity_by_id(self._tree_model_filter.get_value(treeiter, 0))
        self._app.open_external_app(AppActivityAnalytic, {"activity": activity})

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
        # TODO I need to know how to remove the child now in Gtk4
        # if self._activity_stats_widget and self._activity_stats_widget.get_child():
        #     self._activity_stats_widget.remove(
        #         self._activity_stats_widget.get_child()
        #     )
        self._activity_stats_widget.set_child(widget)

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

