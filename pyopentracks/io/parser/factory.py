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
from itertools import chain

from pyopentracks.io.parser.fit.messages import FitSportMessage, FIT_SUPPORTED_SPORTS
from pyopentracks.io.parser.parser import Parser
from pyopentracks.io.parser.exceptions import FitParserException, ParserExtensionUnknownException, GpxParserException
from pyopentracks.io.parser.gpx.gpx import GpxOpenTracks, GpxPath, GpxStandard, PreParser as GpxPreParser
from pyopentracks.io.parser.fit.fit import (
    PreParser as FitPreParser,
    FitTrackActivity,
    FitSetActivity,
    FitMultisportActivity
)


class ParserFactory:
    """Creates a parser from a file's name.
    
    It uses abstract factory pattern to create the parser that can parse the
    file.
    """

    @staticmethod
    def make(filename: str):
        if filename.endswith(".gpx"):
            return GpxFactory().make(filename)
        elif filename.endswith(".fit"):
            return FitFactory().make(filename)
        else:
            raise ParserExtensionUnknownException(f"File extension unknown: {filename}")


class Factory(ABC):
    """Abstract factory class."""

    @abstractmethod
    def make(self, filename: str) -> Parser:
        pass


class GpxFactory(Factory):
    """GPX factory that creates the parser needed.
    
    It has to parse the GPX (first step) to know what kind of GPX it is.
    """

    def make(self, filename: str) -> Parser:
        record = GpxPreParser(filename).parse()
        all_points = list(chain(*[ s.points for s in record.segments ]))
        if not list(filter(lambda p: p.time or (p.latitude and p.longitude), all_points)):
            raise GpxParserException(filename, "there are not valid points in the GPX file")
        elif not list(filter(lambda p: p.time, all_points)):
            return GpxPath(record)
        elif record.recorded_with.is_opentracks():
            return GpxOpenTracks(record)
        else:
            return GpxStandard(record)

class FitFactory(Factory):
    """FIT factory that creates the parser needed."""

    def make(self, filename: str) -> Parser:
        fitfile, file_id = FitPreParser(filename).parse()

        sport_messages = [FitSportMessage(mesg) for mesg in list(fitfile.get_messages("sport"))]

        if self._is_track_activity(sport_messages):
            return FitTrackActivity(fitfile.messages, file_id, sport_messages[0])
        elif self._is_set_activity(sport_messages):
            return FitSetActivity(fitfile.messages, file_id, sport_messages[0])
        elif self._is_multisport_activity(sport_messages):
            return FitMultisportActivity(fitfile.messages, file_id, sport_messages)
        else:
            raise FitParserException(
                filename,
                f"{sport_messages[0]} sport not supported" if len(sport_messages) == 1 else f"FIT file not supported"
            )

    def _is_track_activity(self, sport_messages: list[FitSportMessage]) -> bool:
        if len(sport_messages) != 1:
            return False
        return sport_messages[0].category in FIT_SUPPORTED_SPORTS["with_points"]

    def _is_set_activity(self, sport_messages: list[FitSportMessage]) -> bool:
        if len(sport_messages) != 1:
            return False
        return sport_messages[0].category in FIT_SUPPORTED_SPORTS["with_sets"]

    def _is_multisport_activity(self, sport_messages: list[FitSportMessage]) -> bool:
        """It's a multisport activity if there are several sports and they are supported ones."""
        if len(sport_messages) < 2:
            return False
        categories = (
            FIT_SUPPORTED_SPORTS["with_points"] +
            FIT_SUPPORTED_SPORTS["with_sets"] +
            FIT_SUPPORTED_SPORTS['transition']
        )
        return len([mesg for mesg in sport_messages if mesg.category in categories]) == len(sport_messages)
