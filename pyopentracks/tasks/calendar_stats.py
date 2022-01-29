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

import calendar

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import DateTimeUtils as dtu


class CalendarStats:

    class Day:
        def __init__(self, tracks, day, column, row):
            self.tracks = tracks
            self.day = day
            self.column = column
            self.row = row

    class Week:
        def __init__(self, week, aggregated_list, max_value):
            self.week = week
            self.aggregated_list = aggregated_list
            self.max_value = max_value

    def __init__(self):
        self.days = []
        self.weeks = []

    @staticmethod
    def run(month, year):
        obj = CalendarStats()
        row = 1
        column = 0
        aggregated_lists = []
        for week in calendar.monthcalendar(year, month):
            for day in week:
                if day != 0:
                    tracks = DatabaseHelper.get_tracks_in_day(year, month, day)
                    obj.days.append(CalendarStats.Day(tracks, day, column, row))
                column = column + 1
            aggregated_lists.append(
                DatabaseHelper.get_aggregated_stats(
                    dtu.begin_of_day(year, month, list(filter(lambda d: d != 0, week))[0]),
                    dtu.end_of_day(year, month, list(filter(lambda d: d != 0, week))[-1]),
                    order_by_categories=True
                )
            )
            row = row + 1
            column = 0

        max_moving_time = max(
            list(
                map(
                    lambda ltimes: sum(ltimes),
                    list(
                        map(
                            lambda alist: list(
                                map(
                                    lambda o: o.total_moving_time_ms,
                                    alist
                                )
                            ) if alist else [0],
                            aggregated_lists
                        )
                    )
                )
            )
        )
        for i, aggregated_list in enumerate(aggregated_lists):
            obj.weeks.append(CalendarStats.Week(i + 1, aggregated_list, max_moving_time))
        return obj
