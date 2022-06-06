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

from pyopentracks.app_external import AppExternal
from pyopentracks.app_interfaces import Action
from pyopentracks.app_track_list_interfaces import ActionsTuple
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.layouts.greeter_layout import GreeterLayout
from pyopentracks.views.layouts.tracks_layout import TracksLayout, TracksContainerLayout


class AppTrackList(AppExternal):
    """Handler of list of tracks App."""

    def __init__(self, app):
        """
        Arguments:
        app -- pyopentracks.Application object.
        """
        super().__init__()
        self._app = app
        self._layout = TracksContainerLayout()
        tracks = DatabaseHelper.get_tracks()
        self._actions = {}
        if tracks and len(tracks) > 0:
            self._layout.set_child(TracksLayout(app=self, tracks=DatabaseHelper.get_tracks()))
        else:
            self._layout.set_child(GreeterLayout())
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
        self._layout.set_child(GreeterLayout())

    def get_window(self):
        return self._app.get_window()

    def open_external_app(self, class_var, dict_args):
        self._app.open_external_app(class_var, dict_args)
