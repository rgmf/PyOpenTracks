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
from pyopentracks.views.layouts.notebook_layout import NotebookLayout
from pyopentracks.views.layouts.segments_list_layout import SegmentsListLayout
from pyopentracks.app_external import AppExternal


class AppSegments(AppExternal):
    """Handler of Segments App.

    This is the controller of the segment's views.
    """

    def __init__(self):
        self._layout = NotebookLayout()
        self._layout.append(SegmentsListLayout.from_segments(), _("Segment's List"))

    def get_layout(self):
        return self._layout
