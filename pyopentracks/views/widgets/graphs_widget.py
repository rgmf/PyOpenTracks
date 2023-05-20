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
from gi.repository import Gtk

from abc import ABC, abstractmethod
from collections import namedtuple

from pyopentracks.utils.utils import TypeActivityUtils as tau
from pyopentracks.utils.utils import DistanceUtils as distu
from pyopentracks.utils.utils import DateTimeUtils as dtu
from pyopentracks.utils.utils import DateUtils as du
from pyopentracks.utils.utils import TimeUtils as tu
from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.views.graphs import BarsChart


ChartValue = namedtuple("ChartValue", ["category", "value"])


class ChartWidget(Gtk.Box):

    def __init__(self, data: dict):
        """Create a ChartWidget with data.

        Arguments:
        data -- is a dictionary which values are a list of ChartValue.
                Something like this:
                {
                    "key1": [("category1", "value1"), ...],
                    "key2": [("category2", "value2"), ...],
                    ...
                }
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._data = data
        self._callback_annotation = None

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def add(self, widget_description: str):
        pass

    def set_category(self, category: str):
        self._data = {
            k: [chart_value for chart_value in chart_values if chart_value.category == category]
            for k, chart_values in self._data.items()
        }

    def set_callback_for_chart_annotation(self, cb):
        self._callback_annotation = cb


class YearlyChartWidget(ChartWidget):

    def __init__(self, data: dict):
        super().__init__(data)
        self._categories_filter = None

    def draw(self):
        graph_data = {}
        if self._categories_filter is not None:
            graph_data = {
                key: sum([
                    chart_value.value for chart_value in values
                    if chart_value.category in self._categories_filter
                ]) for key, values in self._data.items()
            }
        else:
            graph_data = {
                key: sum([value.value for value in values]) for key, values in self._data.items()
            }

        graph = BarsChart(
            graph_data,
            orientation="vertical",
            height_ratio=3,
            cb_annotate=self._callback_annotation
        )
        self.append(graph.get_canvas())
        graph.draw_and_show()

    def add(self, widget_description: str):
        if widget_description == "categories_filter":
            self._append_categories_filter()

    def _append_categories_filter(self):
        self._categories_filter = list({
            chart_value.category for values_list in self._data.values()
            for chart_value in values_list if chart_value.category is not None
        })

        category_buttons = [
            self._create_button(category) for category in self._categories_filter
        ]

        toggle_buttons_box = Gtk.Box()
        toggle_buttons_box.set_margin_start(45)
        toggle_buttons_box.set_margin_top(20)
        for b in category_buttons:
            toggle_buttons_box.append(b)

        self.append(toggle_buttons_box)

    def _create_button(self, category: str) -> Gtk.ToggleButton:
        icon = Gtk.Image()
        icon.set_from_pixbuf(tau.get_icon_pixbuf(category))
        icon.set_pixel_size(24)
        icon.set_margin_top(10)
        icon.set_margin_bottom(10)
        icon.set_margin_start(10)
        icon.set_margin_end(10)

        button = Gtk.ToggleButton()
        button.set_active(True)
        button.connect("toggled", self._on_button_toggled, category)
        button.set_margin_start(5)
        button.set_child(icon)

        return button

    def _on_button_toggled(self, button, category):
        if button.props.active:
            self._categories_filter.append(category)
        else:
            self._categories_filter = list(filter(lambda cfilter: cfilter != category, self._categories_filter))
        child = self.get_last_child()
        self.remove(child)
        self.draw()


class ChartBuilder(ABC):
    @abstractmethod
    def build_widget(self) -> ChartWidget:
        pass


class YearlyAggregatedStatsChartBuilder(ChartBuilder):

    def __init__(self, year: int):
        super().__init__()
        self._year = year
        self._all_data = {}
        self._data = {}
        self._type_of_activity = "distance_activities"
        self._callback = None
        self._categories_filter = False

        for month in range(1, 13):
            as_month_list = DatabaseHelper.get_aggregated_stats(
                dtu.first_day_ms(self._year, month),
                dtu.last_day_ms(self._year, month)
            )
            month_name = du.get_month_abbr(month)
            self._all_data[month_name] = {
                "distance_activities": {
                    "total_activities": [
                        ChartValue(a.category, a.total_activities)
                        for a in as_month_list
                        if a.total_activities is not None and a.total_distance_float is not None
                    ] if as_month_list else [ChartValue(None, 0)],
                    "distance": [
                        ChartValue(a.category, a.total_distance_m)
                        for a in as_month_list
                        if a.total_distance_m is not None and a.total_distance_float is not None
                    ] if as_month_list else [ChartValue(None, 0)],
                    "moving_time": [
                        ChartValue(a.category, a.total_moving_time_ms)
                        for a in as_month_list
                        if a.total_moving_time_ms is not None and a.total_distance_float is not None
                    ] if as_month_list else [ChartValue(None, 0)]
                },
                "time_activities": {
                    "total_activities": [
                        ChartValue(a.category, a.total_activities)
                        for a in as_month_list
                        if a.total_activities is not None and a.total_distance_float is None
                    ] if as_month_list else [ChartValue(None, 0)],
                    "moving_time": [
                        ChartValue(a.category, a.total_moving_time_ms)
                        for a in as_month_list
                        if a.total_moving_time_ms is not None and a.total_distance_float is None
                    ] if as_month_list else [ChartValue(None, 0)]
                }
            }

    def set_activity_distance(self):
        self._type_of_activity = "distance_activities"
        return self

    def set_activity_time(self):
        self._type_of_activity = "time_activities"
        return self

    def set_distance(self):
        self._data = {}
        self._callback = None

        if self._type_of_activity == "time_activities":
            return self

        self._callback = distu.m_to_int_str
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["distance"]
        return self

    def set_moving_time(self):
        self._data = {}
        self._callback = tu.ms_to_inline_shorten_str
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["moving_time"]
        return self

    def set_total_activities(self):
        self._data = {}
        self._callback = round
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["total_activities"]
        return self

    def set_category_filter(self, category: str = None):
        self._category = category
        self._categories_filter = True if category is None else False
        return self

    def build_widget(self) -> ChartWidget:
        chart_widget = YearlyChartWidget(self._data)
        chart_widget.set_callback_for_chart_annotation(self._callback)
        if self._categories_filter:
            chart_widget.add("categories_filter")
        if self._category is not None:
            chart_widget.set_category(self._category)
        return chart_widget


class AllTimesAggregatedStatsChartBuilder(ChartBuilder):

    def __init__(self, aggregated_stats=None):
        super().__init__()
        self._all_data = {}
        self._data = {}
        self._type_of_activity = "distance_activities"
        self._category = None
        self._callback = None
        self._categories_filter = False

        for year_str in DatabaseHelper.get_years(order="ASC"):
            as_year_list = DatabaseHelper.get_aggregated_stats(
                dtu.first_day_ms(int(year_str), 1),
                dtu.last_day_ms(int(year_str), 12)
            )
            self._all_data[int(year_str)] = {
                "distance_activities": {
                    "total_activities": [
                        ChartValue(a.category, a.total_activities)
                        for a in as_year_list
                        if a.total_activities is not None and a.total_distance_float is not None
                    ] if as_year_list else [ChartValue(None, 0)],
                    "distance": [
                        ChartValue(a.category, a.total_distance_m)
                        for a in as_year_list
                        if a.total_distance_m is not None and a.total_distance_float is not None
                    ] if as_year_list else [ChartValue(None, 0)],
                    "moving_time": [
                        ChartValue(a.category, a.total_moving_time_ms)
                        for a in as_year_list
                        if a.total_moving_time_ms is not None and a.total_distance_float is not None
                    ] if as_year_list else [ChartValue(None, 0)]
                },
                "time_activities": {
                    "total_activities": [
                        ChartValue(a.category, a.total_activities)
                        for a in as_year_list
                        if a.total_activities is not None and a.total_distance_float is None
                    ] if as_year_list else [ChartValue(None, 0)],
                    "moving_time": [
                        ChartValue(a.category, a.total_moving_time_ms)
                        for a in as_year_list
                        if a.total_moving_time_ms is not None and a.total_distance_float is None
                    ] if as_year_list else [ChartValue(None, 0)]
                }
            }

    def set_activity_distance(self):
        self._type_of_activity = "distance_activities"
        return self

    def set_activity_time(self):
        self._type_of_activity = "time_activities"
        return self

    def set_distance(self):
        self._data = {}
        self._callback = None

        if self._type_of_activity == "time_activities":
            return self

        self._callback = distu.m_to_int_str
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["distance"]
        return self

    def set_moving_time(self):
        self._data = {}
        self._callback = tu.ms_to_inline_shorten_str
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["moving_time"]
        return self

    def set_total_activities(self):
        self._data = {}
        self._callback = round
        for k, v in self._all_data.items():
            self._data[k] = v[self._type_of_activity]["total_activities"]
        return self

    def set_category_filter(self, category: str = None):
        self._category = category
        self._categories_filter = True if category is None else False
        return self

    def build_widget(self) -> ChartWidget:
        chart_widget = YearlyChartWidget(self._data)
        chart_widget.set_callback_for_chart_annotation(self._callback)
        if self._categories_filter:
            chart_widget.add("categories_filter")
        if self._category is not None:
            chart_widget.set_category(self._category)
        return chart_widget
