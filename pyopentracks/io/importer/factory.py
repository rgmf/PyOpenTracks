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
import os

from pyopentracks.io.importer.file_importer import FileImporter
from pyopentracks.io.importer.folder_importer import FolderImporter
from pyopentracks.io.importer.importer import Importer


class ImporterFactory:

    @staticmethod
    def make(file: str) -> Importer:
        """Makes an importer according to the file.
        
        Arguments:
            file -- it can be a regular file or a directory.
        """
        if os.path.isdir(file):
            return FolderImporter(file)
        elif os.path.isfile(file):
            return FileImporter(file)
        else:
            raise Exception(str(file) + " is not a file or directory")
