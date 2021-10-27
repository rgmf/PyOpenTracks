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

import threading
from os import path

from gi.repository import GLib, GObject

from pyopentracks.models.database_helper import DatabaseHelper
from pyopentracks.utils.utils import TimeUtils
from pyopentracks.io.result import Result


class ExportTrack():
    def __init__(self, trackid, folder):
        self._trackid = trackid
        self._track = DatabaseHelper.get_track_by_id(trackid)
        self._folder = folder
        self._segment = None

    def run(self):
        if not self._track:
            return Result(code=Result.ERROR, message=_(f"Error: there are not tracks identified by {self._trackid}"))
        trackpoints = DatabaseHelper.get_track_points(self._track.id)
        if not trackpoints or len(trackpoints) == 0:
            return Result(code=Result.ERROR, message=_(f"Error: there are not track points into track identified by {self._trackid}"))

        try:
            with open(path.join(self._folder, str(self._track.id) + self._track.name + ".gpx"), "w") as gpx:
                self._segment = trackpoints[0].segment
                segment_buffer = []

                gpx.write(self._header)
                gpx.write(self._metadata)
                gpx.write(self._open_track)
                gpx.write(self._extensions)
                for tp in trackpoints:
                    if self._segment != tp.segment:
                        self._segment = tp.segment
                        if len(segment_buffer) > 1:
                            gpx.write("<trkseg>\n")
                            for i in segment_buffer:
                                gpx.write(self._trkpt(i))
                            gpx.write("</trkseg>\n")
                        segment_buffer = []
                    segment_buffer.append(tp)
                if len(segment_buffer) > 1:
                    gpx.write("<trkseg>\n")
                    for i in segment_buffer:
                        gpx.write(self._trkpt(i))
                    gpx.write("</trkseg>\n")
                gpx.write(self._close_track)
                gpx.write(self._footer)
        except Exception as e:
            # TODO use here logger
            return Result(code=Result.ERROR, message=_(f"Error exporting the track {self._track.name}: {e}"))
        return Result(code=Result.OK, message=_(f"Track {self._track.name} exported correctly"))

    @property
    def _header(self):
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" \
            "<gpx\n" \
            "version=\"1.1\"\n" \
            "creator=\"PyOpenTracks\"\n" \
            "xmlns=\"http://www.topografix.com/GPX/1/1\"\n" \
            "xmlns:topografix=\"http://www.topografix.com/GPX/Private/TopoGrafix/0/1\"\n" \
            "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" \
            "xmlns:opentracks=\"http://opentracksapp.com/xmlschemas/v1\"\n" \
            "xmlns:gpxtpx=\"http://www.garmin.com/xmlschemas/TrackPointExtension/v2\"\n" \
            "xmlns:pwr=\"http://www.garmin.com/xmlschemas/PowerExtension/v1\"\n" \
            "xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd " \
                "http://www.topografix.com/GPX/Private/TopoGrafix/0/1 http://www.topografix.com/GPX/Private/TopoGrafix/0/1/topografix.xsd " \
                "http://www.garmin.com/xmlschemas/TrackPointExtension/v2 https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd " \
                "http://www.garmin.com/xmlschemas/PowerExtension/v1 https://www8.garmin.com/xmlschemas/PowerExtensionv1.xsd " \
                "http://opentracksapp.com/xmlschemas/v1 http://opentracksapp.com/xmlschemas/OpenTracks_v1.xsd\">\n"

    @property
    def _metadata(self):
        return "<metadata>\n" \
            f"<name>{self._track.name}</name>\n" \
            f"<time>{TimeUtils.ms_to_iso(self._track.start_time_ms)}</time>\n" \
            f"<desc>{self._track.description}</desc>\n" \
            f"<type>{self._track.activity_type}</type>\n" \
            "</metadata>\n"

    @property
    def _open_track(self):
        return "<trk>\n"

    @property
    def _extensions(self):
        if self._track and self._track.uuid:
            return "<extensions>\n" \
                f"<opentracks:trackid>{self._track.uuid}</opentracks:trackid>\n" \
                "</extensions>\n"
        return ""

    @property
    def _close_track(self):
        return "</trk>\n"

    @property
    def _footer(self):
        return "</gpx>"

    def _trkpt(self, tp):
        result = f"<trkpt lat=\"{tp.latitude}\" lon=\"{tp.longitude}\">\n"
        result = result + f"<time>{TimeUtils.ms_to_iso(tp.time_ms)}</time>\n"
        if tp.speed_mps is not None:
            result = result + f"<gpxtpx:speed>{tp.speed_mps}</gpxtpx:speed>\n"
        if tp.altitude is not None:
            result = result + f"<ele>{tp.altitude}</ele>\n"
        if tp.elevation_gain is not None:
            result = result + f"<gpxtpx:gain>{tp.elevation_gain}</gpxtpx:gain>\n"
        if tp.elevation_loss is not None:
            result = result + f"<gpxtpx:loss>{tp.elevation_loss}</gpxtpx:loss>\n"
        if tp.heart_rate is not None:
            result = result + f"<gpxtpx:hr>{tp.heart_rate}</gpxtpx:hr>\n"
        if tp.cadence is not None:
            result = result + f"<gpxtpx:cad>{tp.cadence}</gpxtpx:cad>\n"
        result = result + "</trkpt>\n"
        return result


class ExportAllHandler(GObject.GObject):

    __gsignals__ = {
        "total-tracks-to-export": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self, path, cb):
        GObject.GObject.__init__(self)
        self._folder = path
        self._callback = cb

    def run(self):
        threading.Thread(target=self._export_in_thread, daemon=True).start()

    def _export_in_thread(self):
        tracks = DatabaseHelper.get_tracks()
        self.emit("total-tracks-to-export", len(tracks))
        for track in DatabaseHelper.get_tracks():
            result = ExportTrack(track.id, self._folder).run()
            GLib.idle_add(self._callback, result)
