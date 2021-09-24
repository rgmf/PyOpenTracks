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

import urllib.request
import json
import math
import collections

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import LocationUtils


class AltitudeCorrection:
    """
    It uses Open Elevation API to correct track points altitudes and compute gain, loss, min and max altitudes.
    It also updates data in the database (tracks and trackpoints).
    """

    BULK_NUM = 500
    API_BASE_URL = "https://api.open-elevation.com/api/v1/lookup"
    GAIN_LOSS_THRESHOLD = 5
    DISTANCE_TRHESHOLD = 50
    CIRCULAR_BUFFER_LEN = 20

    def __init__(self, trackid):
        super().__init__()
        self._trackid = trackid
        self._max = 0
        self._min = 0
        self._gain = 0
        self._loss = 0
        self._trackpoints = DatabaseHelper.get_track_points(self._trackid)
        self._buffer = collections.deque(maxlen=AltitudeCorrection.CIRCULAR_BUFFER_LEN)
        self._altitudes = []

    def run(self):
        if not self._trackpoints:
            return
        self._init_buffer()
        self._update_track_points()
        self._compute_gain_and_loss()
        self._update_track_stats()
        return DatabaseHelper.get_track_by_id(self._trackid)

    def _init_buffer(self):
        n = 20 if len(self._trackpoints) >= 20 else len(self._trackpoints)
        for i in range(n):
            self._buffer.append(self._trackpoints[i].altitude)

    def _update_track_points(self):
        for i in range(math.ceil(len(self._trackpoints) / AltitudeCorrection.BULK_NUM)):
            locations = []
            for tp in self._trackpoints[
                      i * AltitudeCorrection.BULK_NUM:i * AltitudeCorrection.BULK_NUM + AltitudeCorrection.BULK_NUM]:
                locations.append({"latitude": tp.latitude, "longitude": tp.longitude})
            json_data = json.dumps({"locations": locations}, skipkeys=int).encode("utf-8")
            request = urllib.request.Request(
                AltitudeCorrection.API_BASE_URL, json_data, method="POST", headers={"Content-Type": "application/json"}
            )
            response = urllib.request.urlopen(request)
            res_byte = response.read()
            res_str = res_byte.decode("utf8")
            js_str = json.loads(res_str)
            response.close()

            DatabaseHelper.update_altitude(self._trackid, js_str["results"])
        self._trackpoints = DatabaseHelper.get_track_points(self._trackid)

    def _compute_gain_and_loss(self):
        last_valid_tp = self._trackpoints[0]
        last_valid_altitude = round(sum(self._buffer) / AltitudeCorrection.CIRCULAR_BUFFER_LEN, 2)
        for tp in self._trackpoints:
            if LocationUtils.distance_between(last_valid_tp.latitude, last_valid_tp.longitude, tp.latitude, tp.longitude) >= AltitudeCorrection.DISTANCE_TRHESHOLD:
                if tp.altitude >= last_valid_altitude + AltitudeCorrection.GAIN_LOSS_THRESHOLD:
                    diff = tp.altitude - last_valid_tp.altitude
                    self._gain += diff
                    last_valid_tp = tp
                    self._buffer.append(tp.altitude)
                    last_valid_altitude = round(sum(self._buffer) / AltitudeCorrection.CIRCULAR_BUFFER_LEN, 2)
                    last_valid_tp.set_elevation_gain(diff)
                    DatabaseHelper.update(last_valid_tp)
                elif tp.altitude <= last_valid_altitude - AltitudeCorrection.GAIN_LOSS_THRESHOLD:
                    diff = last_valid_tp.altitude - tp.altitude
                    self._loss += diff
                    last_valid_tp = tp
                    self._buffer.append(tp.altitude)
                    last_valid_altitude = round(sum(self._buffer) / AltitudeCorrection.CIRCULAR_BUFFER_LEN, 2)
                    last_valid_tp.set_elevation_loss(diff)
                    DatabaseHelper.update(last_valid_tp)
            if self._min > tp.altitude:
                self._min = tp.altitude
            if self._max < tp.altitude:
                self._max = tp.altitude

    def _update_track_stats(self):
        DatabaseHelper.update_stats(self._trackid, self._min, self._max, self._gain, self._loss)
