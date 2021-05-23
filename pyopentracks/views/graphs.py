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

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas
)
from pyopentracks.utils.utils import DistanceUtils as du


class AggregatedStatsChart:
    def __init__(self, aggregated_lists):
        categories = [a.category for a in aggregated_lists]
        distances = [a.total_distance_float for a in aggregated_lists]

        self.figure = Figure()
        self.figure.subplots()
        self.axes = self.figure.axes[0]
        self.figure.canvas = FigureCanvas(self.figure)
        self.axes.spines["left"].set_visible(False)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["bottom"].set_visible(False)
        self.axes.spines["top"].set_visible(False)
        self.axes.tick_params(left=False)
        self.axes.tick_params(bottom=False)
        self.axes.set_xlim([0, max(distances) + max(distances) * 0.25])
        self.figure.patch.set_alpha(0)
        self.axes.patch.set_alpha(0)

        y_pos = np.arange(len(categories))
        rectangles = self.axes.barh(y_pos, distances)
        self.axes.set_yticks(y_pos)
        self.axes.set_yticklabels(categories)
        # Turn off x tick labels
        self.axes.set_xticklabels([])
        #self.axes.invert_yaxis()  # labels read top-to-bottom

        #rect_labels = []
        # Lastly, write in the ranking inside each bar to aid in interpretation
        for rect in rectangles:
            # Rectangle width
            width = rect.get_width()

            # Shift the text to the right side of the right edge
            xloc = 5
            # Black against white background
            clr = 'black'
            align = 'left'

            # Center the text vertically in the bar
            y_loc = rect.get_y() + rect.get_height() / 2
            label = self.axes.annotate(
                du.m_to_str(width * 1000),
                xy=(width, y_loc),
                xytext=(xloc, 0),
                textcoords="offset points",
                horizontalalignment=align,
                verticalalignment='center',
                color=clr,
                weight='bold',
                clip_on=True
            )
            #rect_labels.append(label)

        self.figure.canvas.set_size_request(300, 200)
        self.figure.canvas.set_has_window(False)

    def get_canvas(self):
        return self.figure.canvas

    def draw_and_show(self):
        self.figure.canvas.draw()
        self.figure.canvas.show()


class LinePlot:
    def __init__(self, xvalues, yvalues):
        self._xvalues = xvalues
        self._yvalues = yvalues

        self.figure = Figure()
        self.figure.subplots()

        self.figure.canvas = FigureCanvas(self.figure)

        self.axes = self.figure.axes[0]
        self.axes.spines["left"].set_visible(True)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["bottom"].set_visible(True)
        self.axes.spines["top"].set_visible(False)
        #self.axes.plot([0, 200],[50, 50],'--g',label='min: '+str(50)+' m')
        self.axes.fill_between(xvalues, 0, yvalues, facecolor="green", alpha=0.5)

        self.figure.canvas.set_size_request(300, 200)
        self.figure.canvas.set_has_window(False)

    def get_canvas(self):
        return self.figure.canvas

    def draw_and_show(self):
        self.figure.canvas.draw()
        self.figure.canvas.show()
