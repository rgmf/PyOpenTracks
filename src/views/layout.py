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

from pyopentracks.views.maps import TrackMap
from pyopentracks.utils.utils import TypeActivityUtils as TAU
from pyopentracks.models.database import Database
from pyopentracks.io.gpx_parser import GpxLocationsHandle


class Layout():
    def __init__(self):
        self._top_widget = None
        self._main_widget = None
        self._bottom_widget = None

    def get_top_widget(self):
        raise NotImplementedError


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/greeter_layout.ui")
class GreeterLayout(Gtk.Box, Layout):
    __gtype_name__ = "GreeterLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.show_all()

    def _setup_ui(self):
        helptext = _("You can:\n1.- Import a folder with tracks.\n2.- Import a track's file.\n3.- Select a folder to synchronize the tracks files inside it.")
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_homogeneous(False)
        labelh1 = Gtk.Label(label=_("Welcome to PyOpenTracks"))
        labelh1.get_style_context().add_class("pyot-h1")
        labelp = Gtk.Label(label=helptext)
        labelp.get_style_context().add_class("pyot-p-large")
        vbox.pack_start(labelh1, False, False, 0)
        vbox.pack_start(labelp, False, False, 0)
        self._main_widget.pack_start(vbox, True, True, 0)

    def get_top_widget(self):
        return self._top_widget


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/track_stats_layout.ui")
class TrackStatsLayout(Gtk.ScrolledWindow, Layout):
    __gtype_name__ = "TrackStatsLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Grid = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    def get_top_widget(self):
        return self._top_widget

    def load_data(self, track):
        """Load track_stats object into the _main_widget.

        Arguments:
        track -- Track object with stats and all information.
        """
        self._main_widget.foreach(
            lambda child: self._main_widget.remove(child)
        )

        label = Gtk.Label(label=_("Track Stats"))
        label.get_style_context().add_class("pyot-h1")
        self._main_widget.attach(label, 0, 0, 4, 1)

        # Track's name, description and type
        self._add_info_track(track, 0, 1, 2, 1)
        # Start datetime
        self._add_item(_("Start"), track.start_time, 0, 2, 1, 1)
        # End datetime
        self._add_item(_("End"), track.end_time, 1, 2, 1, 1)
        # Total distance
        self._add_item(_("Distance"), track.total_distance, 0, 3, 1, 1)
        # Total moving time
        self._add_item(_("Moving Time"), track.moving_time, 1, 3, 1, 1)
        # Total time
        self._add_item(_("Total Time"), track.total_time, 0, 4, 1, 1)
        # Avg. moving speed
        self._add_item(
            _("Avg. Moving Speed"),
            track.avg_moving_speed, 0, 5, 1, 1)
        # Avg. speed
        self._add_item(_("Avg. Speed"), track.avg_speed, 1, 5, 1, 1)
        # Max. speed
        self._add_item(_("Max. Speed"), track.max_speed, 0, 6, 1, 1)
        # Max. elevation
        self._add_item(_("Max. Altitude"), track.max_elevation, 0, 7, 1, 1)
        # Min. elevation
        self._add_item(_("Min. Altitude"), track.min_elevation, 1, 7, 1, 1)
        # Gain elevation
        self._add_item(_("Elevation Gain"), track.gain_elevation, 0, 8, 1, 1)
        # Loss elevation
        self._add_item(_("Elevation Loss"), track.loss_elevation, 1, 8, 1, 1)

        self.show_all()

    def load_map(self, locations):
        """Load the map with the locations.
        
        Arguments:
        locations -- list of tuple with two items (float):
                     latitude and longitude.
        """
        # Map
        self._add_map(locations, 2, 1, 2, 8)
        self.show_all()

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
            resource_path=TAU.get_icon_resource(track.activity_type),
            width=48,
            height=48,
            preserve_aspect_ratio=True
        )
        icon = Gtk.Image.new_from_pixbuf(pixbuf)

        name_label = Gtk.Label(label=track.name)
        name_label.set_line_wrap(True)
        name_label.set_justify(Gtk.Justification.LEFT)
        name_label.get_style_context().add_class("pyot-stats-header")

        hbox.pack_start(icon, expand=False, fill=True, padding=0)
        hbox.pack_start(name_label, expand=False, fill=True, padding=10)

        desc_label = Gtk.Label(label=track.description)
        desc_label.set_line_wrap(True)
        desc_label.set_justify(Gtk.Justification.LEFT)
        desc_label.get_style_context().add_class("pyot-stats-value")

        vbox.pack_start(hbox, True, True, 0)
        vbox.pack_start(desc_label, True, True, 0)

        self._main_widget.attach(vbox, left, top, width, height)

    def _add_item(
            self, label_text, value, left, top, width, height,
            label_align=Gtk.Justification.CENTER,
            value_align=Gtk.Justification.CENTER
    ):
        """Adds an stat item into the _main_widget (Gtk.Grid).

        Arguments:
        label_text -- the text describing the stats value.
        value -- stat's value.
        left -- the column number to attach the left side of item to.
        top -- the row number to attach the top side of item to.
        width --  the number of columns that item will span.
        height -- the number of rows that item will span.
        label_align -- (optional) justify value for label (center by default).
        value_align -- (optional) justify value for value (center by default).
        """
        vbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        vbox.get_style_context().add_class("pyot-stats-bg-color")
        vbox.set_homogeneous(False)

        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("pyot-stats-header")
        label.set_justify(label_align)

        value = Gtk.Label(label=value)
        value.get_style_context().add_class("pyot-stats-value")
        value.set_justify(value_align)

        vbox.pack_start(label, True, True, 0)
        vbox.pack_start(value, True, True, 0)

        self._main_widget.attach(vbox, left, top, width, height)

    def _add_map(self, locations, left, top, width, height):
        """Adds a map with track_points values into the _main_widget.

        Arguments:
        locations -- a list of locations.
        left -- the column number to attach the left side of map to.
        top -- the row number to attach the top side of map to.
        width --  the number of columns that map will span.
        height -- the number of rows that map will span.
        """
        m = TrackMap(locations)
        scrolled_window = Gtk.ScrolledWindow()
        webview = WebKit2.WebView()
        webview.load_html(m.get_data().getvalue().decode())
        scrolled_window.add(webview)

        self._main_widget.attach(scrolled_window, left, top, width, height)


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/tracks_layout.ui")
class TracksLayout(Gtk.Box, Layout):
    __gtype_name__ = "TracksLayout"

    _top_widget: Gtk.Box = Gtk.Template.Child()
    _main_widget: Gtk.Paned = Gtk.Template.Child()
    _bottom_widget: Gtk.Box = Gtk.Template.Child()

    _list_widget: Gtk.ListBox = Gtk.Template.Child()
    _track_stats_widget: Gtk.ScrolledWindow = Gtk.Template.Child()

    class TrackRow(Gtk.ListBoxRow):
        def __init__(self, _id, path):
            super().__init__()
            self._id = _id
            self._path = path

        @property
        def id(self):
            return self._id

        @property
        def path(self):
            return self._path

    def __init__(self, app, tracks):
        super().__init__()

        self._app = app
        self._db = Database()

        self._list_widget.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list_widget.connect('row-activated', self._on_row_activated)

        self._show_message(_("Select a track to view its stats..."))

        self._tracks = tracks
        self._load_data()

        self.show_all()

    def get_top_widget(self):
        return self._top_widget

    def _load_data(self):
        for track in self._tracks:
            row = TracksLayout.TrackRow(track._id, track.trackfile_path)
            label = Gtk.Label(label=track.name)
            label.set_justify(Gtk.Justification.LEFT)
            label.get_style_context().add_class("pyot-list-tracks-label")
            row.add(label)
            self._list_widget.add(row)

    def _on_row_activated(self, listbox, row):
        track = self._db.get_track_by_id(row.id)
        if not track:
            self._show_message(_("There was an error and the track cannot be showed"))
            return
        self._load_track_stats(track)
        loc_handle = GpxLocationsHandle()
        loc_handle.get_locations(track.trackfile_path, self._on_locations_end)

    def _on_locations_end(self, locations):
        """Load a map with locations.

        Check if there is a TrackStatsLayout widget inside the Viewport
        of the ScrolledWindow _track_stats_widget.

        If all is ready then load map with locations.
        """
        if (
            not self._track_stats_widget or
            not self._track_stats_widget.get_child()
        ):
            return

        child = self._track_stats_widget.get_child().get_child()
        if child and isinstance(child, TrackStatsLayout):
            child.load_map(locations)

    def _load_track_stats(self, track):
        layout = TrackStatsLayout()
        layout.load_data(track)
        self._add_widget(layout)

    def _show_message(self, msg):
        label = Gtk.Label(label=_("Select a track to view its stats..."))
        label.get_style_context().add_class("pyot-h1")
        self._add_widget(label)

    def _add_widget(self, widget):
        """Add the widget to _track_stats_widget.

        Arguments:
        widget -- the widget to add to ScrolledWindow _track_stats_widget.
        """
        if self._track_stats_widget and self._track_stats_widget.get_child():
            self._track_stats_widget.remove(
                self._track_stats_widget.get_child()
            )
        self._track_stats_widget.add(widget)
        self.show_all()
