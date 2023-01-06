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


class GainLossManager:
    """Smooth the elevation gain and loss noise."""

    # Ignore differences of DIFF_THRESHOLD between two consecutive altitudes.
    DIFF_THRESHOLD = 5
    # Elevation accumulation threshold to add gain or loss.
    ACCUM_THRESHOLD = 0.7

    def __init__(self):
        self._last_altitude = None

        self._gain_accum = 0
        self._gain = 0
        self._loss_accum = 0
        self._loss = 0

        self._total_gain = 0
        self._total_loss = 0

    def add(self, altitude):
        if self._last_altitude is None:
            self._last_altitude = altitude
            return

        if altitude is None:
            return

        diff = abs(self._last_altitude - altitude)

        if diff > GainLossManager.DIFF_THRESHOLD:
            self._last_altitude = altitude
            self._gain_accum = self._loss_accum = 0
            return

        if self._last_altitude < altitude:
            self._gain_accum += diff
            self._loss_accum = 0
            if self._gain_accum > GainLossManager.ACCUM_THRESHOLD:
                self._gain += self._gain_accum
                self._gain_accum = 0
        elif self._last_altitude > altitude:
            self._loss_accum += diff
            self._gain_accum = 0
            if self._loss_accum > GainLossManager.ACCUM_THRESHOLD:
                self._loss += self._loss_accum
                self._loss_accum = 0

        self._last_altitude = altitude

    def get_and_reset(self):
        gain, loss = self._gain, self._loss
        self._gain = self._loss = 0
        self._total_gain += gain
        self._total_loss += loss
        return gain, loss

