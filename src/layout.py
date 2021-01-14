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

from gi.repository import Gtk, GdkPixbuf, WebKit2

from .maps import TrackMap
from .utils import TypeActivityUtils


class Layout():
    def __init__(self):
        self._top_widget = None
        self._main_widget = None
        self._bottom_widget = None

    def get_top_widget(self):
        raise NotImplementedError()


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/greeter_layout.ui")
class GreeterLayout(Gtk.Box, Layout):
    __gtype_name__ = "GreeterLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        label = Gtk.Label(label="Select a track")
        label.get_style_context().add_class("pyot-h1")
        self._main_widget.pack_start(label, True, True, 0)

    def get_top_widget(self):
        return self._top_widget


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_layout.ui")
class TrackStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "TrackStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self, app):
        super().__init__()
        self._app = app

    def get_top_widget(self):
        return self._top_widget

    def load_data(self, track):
        """Load track_stats object into the _main_widget.

        Arguments:
        track -- Track object with stats and all information.
        """
        track_stats = track.track_stats

        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        label = Gtk.Label(label="Track Stats")
        label.get_style_context().add_class("pyot-h1")
        self._main_widget.attach(label, 0, 0, 4, 1)

        # Track's name, description and type
        self._add_info_track(track, 0, 1, 2, 1)
        # Start datetime
        self._add_item("Inicio", track_stats.start_time, 0, 2, 1, 1)
        # End datetime
        self._add_item("Fin", track_stats.end_time, 1, 2, 1, 1)
        # Total time
        self._add_item("Tiempo total", track_stats.total_time, 0, 3, 1, 1)
        # Total moving time
        self._add_item(
            "Tiempo total en movimiento", track_stats.moving_time, 1, 3, 1, 1
        )
        # Total distance
        self._add_item(
            "Distancia total", track_stats.total_distance, 0, 4, 1, 1
        )
        # Avg. speed
        self._add_item("Velocidad media", track_stats.avg_speed, 1, 4, 1, 1)
        # Max. speed
        self._add_item("Velocidad máxima", track_stats.max_speed, 0, 5, 1, 1)
        # Max. elevation
        self._add_item("Altitud máxima", track_stats.max_elevation, 1, 5, 1, 1)
        # Min. elevation
        self._add_item("Altitud mínima", track_stats.min_elevation, 0, 6, 1, 1)
        # Gain elevation
        self._add_item("Ganancia de altitud", track_stats.gain_elevation, 1, 6, 1, 1)
        # Loss elevation
        self._add_item("Pérdida de altitud", track_stats.loss_elevation, 0, 7, 1, 1)
        # Map
        self._add_map(track_stats, 2, 1, 2, 7)

    def _add_info_track(self, track, left, top, width, height):
        """Adds track information to main widget.

        track -- Track object.
        left -- the column number to attach the left side of item to.
        top -- the row number to attach the top side of item to.
        width --  the number of columns that item will span.
        height -- the number of rows that item will span.
        """
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)

        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_homogeneous(False)

        pixbuf = GdkPixbuf.Pixbuf.new_from_resource_at_scale(
            resource_path=TypeActivityUtils.get_icon_resource(track.activity_type),
            width=48,
            height=48,
            preserve_aspect_ratio=True
        )
        icon = Gtk.Image.new_from_pixbuf(pixbuf)

        name_label = Gtk.Label(label=track.name)
        name_label.get_style_context().add_class("pyot-stats-header")
        name_label.set_xalign(0.0)

        hbox.pack_start(icon, expand=False, fill=True, padding=0)
        hbox.pack_start(name_label, expand=False, fill=True, padding=10)

        desc_label = Gtk.Label(label=track.description)
        desc_label.get_style_context().add_class("pyot-stats-value")
        desc_label.set_xalign(0.0)

        vbox.pack_start(hbox, True, True, 0)
        vbox.pack_start(desc_label, True, True, 0)

        self._main_widget.attach(vbox, left, top, width, height)

    def _add_item(
            self, label_text, value, left, top, width, height,
            label_align=0.5, value_align=0.5
    ):
        """Adds an stat item into the _main_widget (Gtk.Grid).

        Arguments:
        label_text -- the text describing the stats value.
        value -- stat's value.
        left -- the column number to attach the left side of item to.
        top -- the row number to attach the top side of item to.
        width --  the number of columns that item will span.
        height -- the number of rows that item will span.
        label_align -- (optional) xalign value for label (0.5 by default).
        value_align -- (optional) xalign value for value (0.5 by default).
        """
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)

        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("pyot-stats-header")
        label.set_xalign(label_align)

        value = Gtk.Label(label=value)
        value.get_style_context().add_class("pyot-stats-value")
        value.set_xalign(value_align)

        vbox.pack_start(label, True, True, 0)
        vbox.pack_start(value, True, True, 0)

        self._main_widget.attach(vbox, left, top, width, height)

    def _add_map(self, track_stats, left, top, width, height):
        """Adds a map with track_stats values into the _main_widget.

        Arguments:
        track_stats -- TrackStats's object.
        left -- the column number to attach the left side of map to.
        top -- the row number to attach the top side of map to.
        width --  the number of columns that map will span.
        height -- the number of rows that map will span.
        """
        m = TrackMap(track_stats)
        scrolled_window = Gtk.ScrolledWindow()
        webview = WebKit2.WebView()
        webview.load_html(m.get_data().getvalue().decode())
        scrolled_window.add(webview)

        self._main_widget.attach(scrolled_window, left, top, width, height)
