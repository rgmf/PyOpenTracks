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
from pyopentracks.app_preferences import AppPreferences
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.activity import Activity
from pyopentracks.observers.data_update_observer import DataUpdateSubscription
from pyopentracks.views.layouts.layout_builder import LayoutBuilder
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.track_map_analytic_layout import TrackMapAnalyticLayout
from pyopentracks.views.layouts.track_segments_layout import TrackSegmentsLayout


class AppActivityAnalytic(AppExternal):
    """Handler of Analytics App.

    This is the controller of the analytic's views.
    """

    def __init__(self, activity: Activity):
        super().__init__()
        self._layout = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self._activity: Activity = activity
        self._preferences = AppPreferences()
        self._subscriptions = DataUpdateSubscription()

        if not self._activity.all_track_points:
            ProcessView(self._on_sections_ready, DatabaseHelper.get_sections, (self._activity.id,)).start()
        else:
            self._build()

    def get_layout(self):
        return self._layout

    def get_actions(self) -> List[Action]:
        return []

    def get_kwargs(self) -> dict:
        return {"activity": self._activity}

    def segment_created_notify(self):
        self._subscriptions.notify()

    def _build(self):
        LayoutBuilder(self._on_build_layout_done)\
            .set_type(LayoutBuilder.Layouts.ACTIVITY_ANALYTIC)\
            .set_activity(self._activity)\
            .set_preferences(self._preferences)\
            .make()

    def _on_build_layout_done(self, layout):
        if type(layout) == NotebookLayout:
            for child_layout in layout.get_layouts():
                if type(child_layout) == TrackSegmentsLayout:
                    self._subscriptions.attach(child_layout)
                elif type(child_layout) == TrackMapAnalyticLayout:
                    child_layout.set_new_segment_created_cb(self.segment_created_notify)
                child_layout.build()
                child_layout.post_build()
        layout.build()
        self._layout.append(layout)

    def _on_sections_ready(self, sections):
        self._activity.sections = sections
        self._build()
