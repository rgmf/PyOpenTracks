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
from typing import List

from gi.repository import Gtk

from pyopentracks.app_external import AppExternal
from pyopentracks.app_interfaces import Action
from pyopentracks.app_activity_list_interfaces import ActionsTuple
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.layouts.greeter_layout import GreeterLayout
from pyopentracks.views.layouts.activities_layout import ActivitiesLayout


class AppActivityList(AppExternal):
    """Handler of list of activities App."""

    def __init__(self, app):
        """
        Arguments:
        app -- pyopentracks.Application object.
        """
        super().__init__()
        self._app = app
        self._layout = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        activities = DatabaseHelper.get_activities()
        self._actions = {}
        if activities and len(activities) > 0:
            layout = ActivitiesLayout(app=self, activities=DatabaseHelper.get_activities())
            layout.build()
            self._layout.pack_start(layout, True, True, 0)
        else:
            layout = GreeterLayout()
            layout.build()
            self._layout.pack_start(layout, True, True, 0)
        self._layout.show_all()

    def get_layout(self):
        return self._layout

    def get_actions(self) -> List[Action]:
        return list(self._actions.values())

    def get_kwargs(self) -> dict:
        return {}

    def register_actions(self, actions_tuple: List[ActionsTuple]):
        self._actions = {}
        for at in actions_tuple:
            self._actions[at.action_id] = Action(at.action_id, at.callback, at.args)
        self.emit("actions-changed")

    def empty(self):
        self.register_actions([])
        for child in self._layout.get_children():
            self._layout.remove(child)
        layout = GreeterLayout()
        layout.build()
        self._layout.pack_start(layout, True, True, 10)
        self._layout.show_all()

    def get_window(self):
        return self._app.get_window()

    def open_external_app(self, class_var, dict_args):
        self._app.open_external_app(class_var, dict_args)
