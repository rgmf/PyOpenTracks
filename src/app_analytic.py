"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>

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

from pyopentracks.views.analytic import (
    AnalyticLayout, AggregatedStatsYear, AggregatedStats
)


class AppAnalytic:
    """Handler of Analytics App.

    This is the controller of the analytic's views.
    """

    def __init__(self):
        self._layout = AnalyticLayout()

        self._layout.append(AggregatedStats(), _("Aggregated Stats"))

        aggregated_year = AggregatedStatsYear()
        self._layout.append(aggregated_year, _("Stats by year"))
        aggregated_year.show_today()

    def get_layout(self):
        return self._layout
