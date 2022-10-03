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

from pyopentracks.io.parser.parser import Parser
from pyopentracks.io.parser.exceptions import ParserExtensionUnknownException
from pyopentracks.io.parser.gpx.gpx import GpxOpenTracks, GpxPath, GpxStandard, PreParser as GpxPreParser
from pyopentracks.io.parser.fit.fit import PreParser as FitPreParser


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
        if not list(filter(lambda rp: rp.time, list(chain(*[ s.points for s in record.segments ])))):
            return GpxPath(record)
        elif record.recorded_with.is_opentracks():
            return GpxOpenTracks(record)
        else:
            return GpxStandard(record)

class FitFactory(Factory):
    """FIT factory that creates the parser needed."""

    def make(self, filename: str) -> Parser:
        return FitPreParser(filename).parse()

