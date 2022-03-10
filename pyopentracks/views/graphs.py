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

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas
)


class BarsChart:
    def __init__(self, results, colors=None, cb_annotate=None):
        """Creates a set of bar chart with results dictionary.

        Arguments:
        results -- dictionary with values and labels for all bars to
                   add. For example:
                   {
                        "Label 1": 30,
                        "Label 2": 50,
                        "Label 3": 40
                   }
        colors -- (optional) list of colors to be used for every bar.
        cb_annotate -- (optional) it's a callback to parse the bars
                       annotation. If it's not passed then the values
                       will be used like are.
        """
        self._results = results
        self._colors = colors
        self._cb_annotate = cb_annotate

        self._figure = Figure(figsize=(1 * len(results), 1 * len(results)), dpi=100)
        self._figure.subplots()
        self._axes = self._figure.axes[0]

        w, h = self._figure.get_size_inches()
        dpi_res = self._figure.get_dpi()
        w, h = int(np.ceil(w * dpi_res)), int(np.ceil(h * dpi_res))

        self._figure.canvas = FigureCanvas(self._figure)
        self._figure.canvas.set_size_request(w, h)
        self._figure.canvas.set_has_window(False)

    def _draw(self):
        labels = [label for label, _ in self._results.items()]
        values = [value for _, value in self._results.items()]

        self._axes.spines["left"].set_visible(False)
        self._axes.spines["right"].set_visible(False)
        self._axes.spines["bottom"].set_visible(False)
        self._axes.spines["top"].set_visible(False)
        self._axes.tick_params(left=False)
        self._axes.tick_params(bottom=False)
        self._axes.set_xlim([0, max(values) + max(values) * 0.25])
        self._figure.patch.set_alpha(0)
        self._axes.patch.set_alpha(0)

        y_pos = np.arange(len(labels))
        rectangles = self._axes.barh(y_pos, values)
        self._axes.set_yticks(y_pos)
        self._axes.set_yticklabels(labels)
        # Turn off x tick labels
        self._axes.set_xticklabels([])

        # Lastly, write in the ranking inside each bar to aid in interpretation
        for i, rect in enumerate(rectangles):
            # Set rectangle color
            rect.set_color(
                self._colors[i] if self._colors is not None and len(self._colors) > i else None
            )

            # Rectangle width
            width = rect.get_width()
            # Shift the text to the right side of the right edge
            xloc = 5
            # Black against white background
            color = "black"
            align = "left"
            # Center the text vertically in the bar
            yloc = rect.get_y() + rect.get_height() / 2
            self._axes.annotate(
                self._cb_annotate(width) if self._cb_annotate is not None else width,
                xy=(width, yloc),
                xytext=(xloc, 0),
                textcoords="offset points",
                horizontalalignment=align,
                verticalalignment="center",
                color=color,
                weight="bold",
                clip_on=True
            )

    def get_canvas(self):
        return self._figure.canvas

    def draw_and_show(self):
        self._draw()
        self._figure.canvas.draw()
        self._figure.canvas.show()


class StackedBarsChart:

    def __init__(self, results, colors=None, max_width=None, cb_annotate=None):
        """Creates a set of horizontal bars with the results.

        Arguments:
        results -- a dictionary with the results represented like this
                   (array of values to be stacked):
                   {
                        "Label 1": [15, 10, 20, 30],
                        "Label 2": [22, 8, 15, 20],
                        ...
                   }
        colors -- list of colors to use for stacked bars.
        max_width -- (optional) if included the horizontal bar maximum
                     width will be used, otherwise it will be calculated.
        cb_annotate -- (optional) it's a callback to be called for set
                       the annotation on bar chart.
        """

        self._cb_annotate = cb_annotate

        self._accum = 0
        self._bars = []
        self._annotate = None

        self._figure = Figure(figsize=(1, 1), dpi=100)
        self._figure.subplots()
        self._axes = self._figure.axes[0]

        self._axes.spines["left"].set_visible(False)
        self._axes.spines["right"].set_visible(False)
        self._axes.spines["bottom"].set_visible(False)
        self._axes.spines["top"].set_visible(False)
        self._axes.tick_params(left=False)
        self._axes.tick_params(bottom=False)

        w, h = self._figure.get_size_inches()
        dpi_res = self._figure.get_dpi()
        w, h = int(np.ceil(w * dpi_res)), int(np.ceil(h * dpi_res))

        self._figure.canvas = FigureCanvas(self._figure)
        self._figure.canvas.set_size_request(w, h)

        labels = list(results.keys())
        data = np.array(list(results.values()))
        data_cum = data.cumsum(axis=1)

        self._axes.invert_yaxis()
        self._axes.xaxis.set_visible(False)
        max_x = max_width if max_width else np.sum(data, axis=1).max()
        self._axes.set_xlim([0, max_x + max_x * 0.25])

        # Adds stacked bars if data
        if data is None or len(data) == 0 or len(data[0]) == 0:
            return
        rects = None
        for i in range(len(data[0])):
            widths = data[:, i]
            starts = data_cum[:, i] - widths
            color = colors[i] if colors is not None and len(colors) > i else None
            rects = self._axes.barh(labels, widths, left=starts, height=0.75, color=color)
            # Annotate the stacked bars in the middle of the bar.
            # for bar in rects:
            #     width = bar.get_width()
            #     yloc = bar.get_y() + bar.get_height() / 2
            #     self._axes.annotate(
            #             cb_annotate(width) if cb_annotate else width,
            #             xy=(bar.get_x(), yloc),
            #             xytext=(5, 0),
            #             textcoords="offset points",
            #             horizontalalignment="left",
            #             verticalalignment="center",
            #             color="black",
            #             weight="bold",
            #             clip_on=True
            #         )
            for bar in rects:
                self._bars.append(bar)
                self._accum += bar.get_width()

        # Annotate the stacked bars at the end (out from last bar)
        xloc = 5
        yloc = rects[-1].get_y() + rects[-1].get_height() / 2
        self._annotate = self._axes.annotate(
            cb_annotate(self._accum) if cb_annotate else str(self._accum),
            xy=(self._accum, yloc),
            xytext=(xloc, 0),
            textcoords="offset points",
            horizontalalignment="left",
            verticalalignment="center",
            color="black",
            weight="bold",
            clip_on=True
        )

        self._figure.canvas.mpl_connect(
            "motion_notify_event",
            lambda event: self._on_mouse_hover(event)
        )

    def _update_annotate(self, bar):
        if self._annotate is None:
            return

        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_y() + bar.get_height()
        self._annotate.set_text(
            self._cb_annotate(bar.get_width() if self._cb_annotate else str(bar.get_width()))
        )
        self._annotate.set_color(bar.get_facecolor())
        self._figure.canvas.draw_idle()

    def _on_mouse_hover(self, event):
        if self._annotate is None:
            return

        if event.inaxes == self._axes:
            for bar in self._bars:
                bar_contains_event, details = bar.contains(event)
                if bar_contains_event:
                    self._update_annotate(bar)
                    return

        self._annotate.set_text(
            self._cb_annotate(self._accum) if self._cb_annotate else str(self._accum)
        )
        self._annotate.set_color("black")
        self._figure.canvas.draw_idle()

    def get_canvas(self):
        return self._figure.canvas

    def draw_and_show(self):
        self._figure.canvas.draw()
        self._figure.canvas.show()


class LinePlot:
    EVENT_X_CURSOR_POS = 1

    def __init__(self):
        self._figure = Figure()
        self._figure.subplots()

        self._canvas = FigureCanvas(self._figure)

    def add_values(self, values):
        """Add values to the LinePlot object.

        Arguments:
        values - A list with a dictionary with ditance, elevation,
                 heart rate and location information:
                 {
                   "distance": <value in km>,
                   "elevation": <value in meters>,
                   "hr": <value in bpm>,
                   "location": <Location object>
                 }
        """
        self._xvalues = [item["distance"] for item in values]
        self._yvalues = [item["elevation"] for item in values]
        self._locations = [item["location"] for item in values]

        self._axes = self._figure.axes[0]
        self._axes.spines["left"].set_visible(True)
        self._axes.spines["right"].set_visible(False)
        self._axes.spines["bottom"].set_visible(True)
        self._axes.spines["top"].set_visible(False)
        #self._axes.plot([0, 200],[50, 50],'--g',label='min: '+str(50)+' m')
        self._axes.fill_between(self._xvalues, 0, self._yvalues, facecolor="green", alpha=0.5)

        # Second axes with different top and bottom scales for heart rate.
        yheart_rates = [item["hr"] for item in values]
        if sum(yheart_rates) > 0:
            ax2 = self._axes.twinx()
            ax2.spines["left"].set_visible(False)
            ax2.spines["right"].set_visible(True)
            ax2.spines["bottom"].set_visible(True)
            ax2.spines["top"].set_visible(False)
            ax2.plot(self._xvalues, yheart_rates, color="red")

    def get_canvas(self):
        return self._canvas

    def draw_and_show(self):
        self._canvas.draw()
        self._canvas.show()

    def connect(self, event, cb):
        if event == self.EVENT_X_CURSOR_POS:
            # e.xdata contains the km.
            # x is the self._xvalues index for that km.
            # z is the same that e.xdata (the km).
            self._canvas.mpl_connect("motion_notify_event", lambda e: cb(e.xdata, [ self._locations[x] for x, z in enumerate(self._xvalues) if e.xdata and z == round(e.xdata, 2) ]))
