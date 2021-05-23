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

import io
import folium


class TrackMap(folium.Map):
    def __init__(self, locations):
        if locations:
            super().__init__(location=locations[0], zoom_start=13)
            folium.PolyLine(
                locations=locations,
                popup="Path",
                tooltip="Path",
                color="green"
            ).add_to(self)
        else:
            super().__init__()

        self._data = io.BytesIO()
        self.save(self._data, close_file=False)

    def get_data(self):
        return self._data
