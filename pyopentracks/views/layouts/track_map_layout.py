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
import math

from typing import List

from gi.repository import Gtk, Gdk, GObject, Shumate

from pyopentracks.models.location import Location
from pyopentracks.utils.utils import TrackPointUtils


class TrackMapLayout(Shumate.SimpleMap):
    """A Shumate.SimpleMap to show a track on it.

    This map contains:
    - A Shumate.PathLayer with the points of the track.
    - A Shumate.Marker with a generic location.
    - A Shumate.Marker with the initial point.
    - A Shumate.Marker with the end point.
    """

    def __init__(self):
        super().__init__()

        map_source = Shumate.MapSourceRegistry.new_with_defaults().get_by_id(Shumate.MAP_SOURCE_OSM_MAPNIK)
        self.set_map_source(map_source)

        self._start_marker = self._add_marker_from_icon_name("location-start")
        self._start_marker.hide()
        self._end_marker = self._add_marker_from_icon_name("location-end")
        self._end_marker.hide()
        self._location_marker = self._add_marker_from_icon_name("view-pin-symbolic")
        self._location_marker.hide()

        self._path_layer = Shumate.PathLayer.new(self.get_viewport())
        self.add_overlay_layer(self._path_layer)

    def add_polyline_from_points(self, points: List[Location]) -> None:
        if points is None or len(points) == 0:
            return
        self._path_layer.remove_all()
        for point in points:
            shumate_location = Shumate.Point.new()
            shumate_location.set_location(point.latitude, point.longitude)
            self._path_layer.add_node(shumate_location)
        self.set_start_marker(points[0])
        self.set_end_marker(points[-1])
        self._set_center_and_zoom(points)

    def _add_marker_from_icon_name(self, icon_name: str, location: Location = None) -> Shumate.Marker:
        marker = Shumate.Marker.new()
        marker.set_child(Gtk.Image.new_from_icon_name(icon_name))
        if location is not None:
            marker.set_location(location.latitude, location.longitude)

        marker_layer = Shumate.MarkerLayer.new(self.get_viewport())
        marker_layer.add_marker(marker)

        self.add_overlay_layer(marker_layer)

        return marker

    def _set_center_and_zoom(self, points: List[Location]) -> None:
        """Set map center and zoom based on the path layer bounds.

        Link: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
        FixMe: Improve calculations if poles / 180th meridian is crossed
        """

        def get_latitude_derivation(latitude):
            radians = math.radians(latitude)
            return math.asinh(math.tan(radians)) / math.pi / 2

        def get_latitude_derivation_reverse(latitude_derivation):
            radians = math.atan(math.sinh(latitude_derivation * 2 * math.pi))
            return math.degrees(radians)

        x_coordinates, y_coordinates = zip(*[(point.latitude, point.longitude) for point in points])
        min_latitude = min(x_coordinates)
        min_longitude = min(y_coordinates)
        max_latitude = max(x_coordinates)
        max_longitude = max(y_coordinates)

        min_latitude_derivation = get_latitude_derivation(min_latitude)
        max_latitude_derivation = get_latitude_derivation(max_latitude)
        mean_latitude_derivation = (min_latitude_derivation + max_latitude_derivation) / 2

        latitude_fraction = max_latitude_derivation - min_latitude_derivation
        longitude_fraction = (max_longitude - min_longitude) / 360

        tile_size = self.get_map_source().get_tile_size()
        map_height = 363 * 0.95  # self.get_allocated_height() | Offset
        map_width = 599 * 0.95  # self.get_allocated_width() | Offset

        max_zoom_level = self.get_map_source().get_max_zoom_level()
        latitude_zoom_level = math.log(map_height / tile_size / latitude_fraction) / math.log(2)
        longitude_zoom_level = math.log(map_width / tile_size / longitude_fraction) / math.log(2)
        zoom_level = min(max_zoom_level, latitude_zoom_level, longitude_zoom_level)

        self.get_map().go_to_full(
            get_latitude_derivation_reverse(mean_latitude_derivation),
            (min_longitude + max_longitude) / 2,
            zoom_level
        )

    def add_polyline_from_activity_id(self, activity_id):
        print(activity_id)

    def highlight(self, locations: List[Location]):

        print("hightlight")

    def set_start_marker(self, location: Location):
        self._start_marker.set_location(location.latitude, location.longitude)
        self._start_marker.show()

    def set_end_marker(self, location: Location):
        self._end_marker.set_location(location.latitude, location.longitude)
        self._end_marker.show()

    def set_location_marker(self, location: Location, tag: str):
        self._location_marker.set_location(location.latitude, location.longitude)
        self._location_marker.show()


class TrackInteractiveMapLayout(Gtk.Box, GObject.GObject):

    __gsignals__ = {
        "segment-selected": (GObject.SIGNAL_RUN_FIRST, None, (int, int))
    }

    def __init__(self, track_points):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        GObject.GObject.__init__(self)

        self._track_points = track_points

        self._map_layout = TrackMapLayout()
        self._map_layout.add_polyline_from_points(TrackPointUtils.to_locations(track_points))
        self._map_layout.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        label = Gtk.Label.new(_("Select a segment"))
        label.get_style_context().add_class("pyot-h3")

        self._scale_from = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, len(self._track_points) - 1, 1)
        self._scale_to = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, len(self._track_points) - 1, 1)
        self._scale_to.set_value(len(self._track_points) - 1)

        self._scale_from.connect("value-changed", self._scale_changed)
        self._scale_to.connect("value-changed", self._scale_changed)

        button = Gtk.Button.new_with_label(_("Ok"))
        button.set_halign(Gtk.Align.END)
        button.connect(
            "clicked",
            lambda *_: self.emit(
                "segment-selected",
                self._track_points[int(self._scale_from.get_value())].id,
                self._track_points[int(self._scale_to.get_value())].id
            )
        )

        box.append(label)
        box.append(self._scale_from)
        box.append(self._scale_to)
        box.append(button)

        self.append(box)
        self.append(self._map_layout)

    def _scale_changed(self, range):
        i = int(range.get_value())

        if range == self._scale_from and self._scale_to.get_value() <= i:
            self._scale_to.set_value(i)
        elif range == self._scale_to and self._scale_from.get_value() >= i:
            self._scale_from.set_value(i)

        ifrom = int(self._scale_from.get_value())
        ito = int(self._scale_to.get_value())

        self._map_layout.set_start_marker(self._track_points[ifrom].location)
        self._map_layout.set_end_marker(self._track_points[ito].location)

    def get_selected_track_points(self):
        return self._track_points[int(self._scale_from.get_value()):int(self._scale_to.get_value())]
