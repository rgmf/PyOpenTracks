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
from pyopentracks.views.layouts.analytic_layout import (
    AggregatedStatsYear, AggregatedStatsMonth, AggregatedStats
)
from pyopentracks.app_external import AppExternal
from pyopentracks.views.layouts.notebook_layout import NotebookLayout


class AppAnalytic(AppExternal):
    """Handler of Analytics App.

    This is the controller of the analytic's views.
    """

    def __init__(self):
        super().__init__()
        self._layout = NotebookLayout()
        self._layout.append(AggregatedStatsMonth(), _("Monthly Aggregated Stats"))
        self._layout.append(AggregatedStatsYear(), _("Yearly Aggregated Stats"))
        self._layout.append(AggregatedStats(), _("All Aggregated Stats"))

    def get_layout(self):
        return self._layout

    def get_actions(self) -> List[Action]:
        return []

    def get_kwargs(self) -> dict:
        return {}
