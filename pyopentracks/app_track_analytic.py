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
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.track_analytic_layout import TrackAnalyticLayout
from pyopentracks.views.layouts.track_segments_layout import TrackSegmentsLayout
from pyopentracks.views.layouts.track_summary_layout import TrackSummaryLayout


class AppTrackAnalytic(AppExternal):
    """Handler of Analytics App.

    This is the controller of the analytic's views.
    """

    def __init__(self, track):
        summary_layout = TrackSummaryLayout(track)
        segments_layout = TrackSegmentsLayout(track)
        analytic_layout = TrackAnalyticLayout(track)

        self._layout = NotebookLayout()
        self._layout.append(summary_layout, _("Summary"))
        self._layout.append(segments_layout, _("Segments"))
        self._layout.append(analytic_layout, _("Analytic"))

        summary_layout.build()
        segments_layout.build()
        analytic_layout.build()

    def get_layout(self):
        return self._layout
