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


class ParserExtensionUnknownException(Exception):
    """Exception raised for files with an unknown extension.

    Attributes:
        filename -- the filename
        message  -- explanation of the error
    """

    def __init__(self, filename, message="File extension unknown"):
        self._filename = filename
        self._message = message
        super().__init__(self._message)

    def __str__(self):
        return f"{self._filename} -> {self._message}"


class FitParserException(Exception):
    """Exception raised for FIT parsing errors.

    Attributes:
        filename -- the filename
        message  -- explanation of the error
    """

    def __init__(self, filename, message="Error parsing FIT file"):
        self._filename = filename
        self._message = message
        super().__init__(self._message)

    def __str__(self):
        return f"{self._filename} -> {self._message}"
