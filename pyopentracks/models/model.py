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

from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def insert_query(self):
        pass

    @abstractmethod
    def delete_query(self):
        pass

    @abstractmethod
    def update_query(self):
        pass

    @abstractmethod
    def update_data(self):
        pass

    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def bulk_insert_fields(self, fk_value):
        pass
