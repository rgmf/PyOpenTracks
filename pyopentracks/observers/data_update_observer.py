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

from abc import abstractmethod
from typing import List


class DataUpdateObserver:

    @abstractmethod
    def data_updated_notified(self):
        pass


class DataUpdateSubscription:
    _observers: List[DataUpdateObserver] = []

    def attach(self, observer: DataUpdateObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: DataUpdateObserver):
        self._observers.remove(observer)

    def notify(self):
        for o in self._observers:
            o.data_updated_notified()
