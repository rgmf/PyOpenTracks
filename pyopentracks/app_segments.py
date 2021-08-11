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

from gi.repository import Gtk

from pyopentracks.views.layouts.segments_layout import SegmentsLayout
from pyopentracks.views.layouts.segments_list_layout import SegmentsListLayout
from pyopentracks.app_external import AppExternal


class AppSegments(AppExternal):
    """Handler of Segments App.

    This is the controller of the segments's views.
    """

    def __init__(self):
        self._layout = SegmentsLayout()
        segments_list_layout = SegmentsListLayout.from_segments()
        if segments_list_layout.get_number_rows() > 0:
            self._layout.append(segments_list_layout, _("Segment's List"))
        else:
            self._layout.append(Gtk.Label(_("There are not segments.")), _("Segment's List"))
        #self._layout.append(Gtk.Label("Lista de segmentos"), _("Segment's Map"))

    def get_layout(self):
        return self._layout
