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

from pyopentracks.app_interfaces import Action
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.segments_list_layout import SegmentsListLayout
from pyopentracks.app_external import AppExternal


class AppSegments(AppExternal):
    """Handler of Segments App.

    This is the controller of the segment's views.
    """

    def __init__(self, app):
        super().__init__()
        self._app = app
        self._layout = NotebookLayout()
        segments_list_layout = SegmentsListLayout(app=self)
        segments_list_layout.build()
        self._layout.append(segments_list_layout, _("Segment's List"))
        self._layout.build()

    def get_layout(self):
        return self._layout

    def get_actions(self) -> List[Action]:
        return []

    def get_kwargs(self) -> dict:
        return {}

    def get_window(self):
        return self._app.get_window()
