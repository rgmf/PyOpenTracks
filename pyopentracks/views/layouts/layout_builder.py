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
from enum import Enum
from pyopentracks.app_preferences import AppPreferences

from pyopentracks.models.activity import Activity
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.layouts.error_layout import ErrorLayout
from pyopentracks.views.layouts.layout import Layout
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.process_view import ProcessView
from pyopentracks.views.layouts.activity_summary_layout import (
    ActivitySummaryLayout, ClimbingSetsLayout, SetActivitySetsLayout, SetActivitySummaryLayout, TrackActivitySummaryLayout, TrainingSetsLayout
)
from pyopentracks.views.layouts.summary_sport_layout import SummaryMovingSport, SummaryTimeSport
from pyopentracks.views.layouts.track_activity_data_analytic_layout import TrackActivityDataAnalyticLayout
from pyopentracks.views.layouts.track_map_analytic_layout import TrackMapAnalyticLayout
from pyopentracks.views.layouts.track_segments_layout import TrackSegmentsLayout


class LayoutBuilder:
    """Builds a Layout depending on its configuration in a thread."""

    class Layouts(Enum):
        ACTIVITY_SUMMARY = 1
        ACTIVITY_ANALYTIC = 2
        SPORT_SUMMARY = 3

    def __init__(self, cb):
        self._activity: Activity = None
        self._category: str = None
        self._type = None
        self._preferences = None
        self._callback = cb
        self._args = None

    def set_activity(self, activity: Activity):
        self._activity = activity
        return self

    def set_category(self, category: str):
        self._category = category
        return self

    def set_args(self, args: tuple):
        self._args = args
        return self

    def set_preferences(self, prefs: AppPreferences):
        self._preferences = prefs
        return self

    def set_type(self, type):
        self._type = type
        return self

    def make(self):
        if (self._activity is None and self._category is None) or self._type is None:
            self._callback(ErrorLayout())
        else:
            ProcessView(self._on_make_finish, self._make_in_thread, None).start()

    def _make_in_thread(self) -> Layout:
        if self._type == LayoutBuilder.Layouts.ACTIVITY_SUMMARY and self._activity is not None:
            layout = ActivitySummaryLayoutBuilder(self._activity).make()
        elif self._type == LayoutBuilder.Layouts.ACTIVITY_ANALYTIC and self._activity is not None:
            layout = ActivityAnalyticLayoutBuilder(self._activity, self._preferences).make()
        elif self._type == LayoutBuilder.Layouts.SPORT_SUMMARY and self._category is not None:
            layout = SportSummaryLayoutBuilder(self._category, self._args).make()
        else:
            layout = ErrorLayout()

        return layout

    def _on_make_finish(self, layout: Layout):
        layout.build()
        layout.post_build()
        self._callback(layout)


class ActivitySummaryLayoutBuilder:
    """It builds a summary layout depending on the type of activity."""

    def __init__(self, activity: Activity):
        self._activity: Activity = activity

    def make(self) -> Layout:
        if len(self._activity.sections) == 0:
            self._activity.sections = DatabaseHelper.get_sections(self._activity.id)

        if self._activity.stats and len(self._activity.stats.sets) == 0:
            self._activity.stats.sets = DatabaseHelper.get_sets(self._activity.stats.id)

        if len(self._activity.sections) > 0:
            return TrackActivitySummaryLayout(self._activity)
        elif self._activity.stats and len(self._activity.stats.sets) > 0:
            return SetActivitySummaryLayout(self._activity)\
                .add_sets_layout(SetsLayoutBuilder(self._activity).make())
        else:
            return ActivitySummaryLayout.info_activity(self._activity)


class ActivityAnalyticLayoutBuilder:
    """It builds an activity's analytic layout depending on the type of activity."""

    def __init__(self, activity: Activity, prefs: AppPreferences):
        self._activity: Activity = activity
        self._preferences: AppPreferences = prefs

    def make(self) -> Layout:
        layout = NotebookLayout()
        if len(self._activity.sections) == 0:
            self._activity.sections = DatabaseHelper.get_sections(self._activity.id)

        if len(self._activity.stats.sets) == 0:
            self._activity.stats.sets = DatabaseHelper.get_sets(self._activity.stats.id)

        if len(self._activity.sections) > 0:
            summary_layout = TrackActivitySummaryLayout(self._activity)
            data_analytic_layout = TrackActivityDataAnalyticLayout(self._activity, self._preferences)
            segments_layout = TrackSegmentsLayout(self._activity)
            map_analytic_layout = TrackMapAnalyticLayout(self._activity)
            layout.append(summary_layout, _("Summary"))
            layout.append(data_analytic_layout, _("Data Analytic"))
            layout.append(segments_layout, _("Segments"))
            layout.append(map_analytic_layout, _("Map Analytic"))
            return layout
        elif self._activity.stats and len(self._activity.stats.sets) > 0:
            summary_layout = SetActivitySummaryLayout(self._activity)\
                .add_sets_layout(SetsLayoutBuilder(self._activity).make())
            layout.append(summary_layout, _("Summary"))
            return layout
        else:
            return ActivitySummaryLayout.info_activity(self._activity)


class SetsLayoutBuilder:
    """It builds a sets layout depending on the type of activity."""

    def __init__(self, activity: Activity):
        self._activity: Activity = activity

    def make(self) -> SetActivitySetsLayout:
        if self._activity.category == "rock_climbing":
            return ClimbingSetsLayout(self._activity.stats.sets)
        elif self._activity.category == "training":
            return TrainingSetsLayout(self._activity.stats.sets)
        else:
            return SetActivitySetsLayout()


class SportSummaryLayoutBuilder:
    """It builds a summary layout for sport of the category indicated."""

    def __init__(self, category: str, args: tuple):
        self._category = category
        self._args = args

    def make(self):
        if self._category is None:
            return SummaryMovingSport(*self._args if type(self._args) == tuple else self._args)
        elif self._category in ("rock_climbing", "training"):
            return SummaryTimeSport(*self._args if type(self._args) == tuple else self._args)
        else:
            return SummaryMovingSport(*self._args if type(self._args) == tuple else self._args)
