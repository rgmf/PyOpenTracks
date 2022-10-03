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
from pyopentracks.app_external import AppExternal
from pyopentracks.app_preferences import AppPreferences
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.models.track import Track
from pyopentracks.observers.data_update_observer import DataUpdateSubscription
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.track_data_analytic_layout import TrackDataAnalyticLayout
from pyopentracks.views.layouts.track_map_analytic_layout import TrackMapAnalyticLayout
from pyopentracks.views.layouts.track_segments_layout import TrackSegmentsLayout
from pyopentracks.views.layouts.track_summary_layout import TrackSummaryLayout


class AppTrackAnalytic(AppExternal):
    """Handler of Analytics App.

    This is the controller of the analytic's views.
    """

    def __init__(self, track: Track):
        self._layout = NotebookLayout()
        self._track: Track = track
        self._preferences = AppPreferences()

        if not self._track.all_track_points:
            ProcessView(self._on_sections_ready, DatabaseHelper.get_sections, (self._track.id,)).start()
        else:
            self._build()

    def _build(self):
        summary_layout = TrackSummaryLayout(self._track)
        data_analytic_layout = TrackDataAnalyticLayout(self._track, self._preferences)
        segments_layout = TrackSegmentsLayout(self._track)
        map_analytic_layout = TrackMapAnalyticLayout(self._track, self.segment_created_notify)

        self._subscriptions = DataUpdateSubscription()
        self._subscriptions.attach(segments_layout)

        self._layout.append(summary_layout, _("Summary"))
        self._layout.append(data_analytic_layout, _("Data Analytic"))
        self._layout.append(segments_layout, _("Segments"))
        self._layout.append(map_analytic_layout, _("Map Analytic"))

        summary_layout.build()
        data_analytic_layout.build()
        segments_layout.build()
        map_analytic_layout.build()

    def _on_sections_ready(self, sections):
        self._track.sections = sections
        self._build()

    def get_layout(self):
        return self._layout

    def segment_created_notify(self):
        self._subscriptions.notify()
