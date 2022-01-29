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

import logging
import sys

from pyopentracks import settings


def initialize(loglevel: int):
    """Initialize logger and return the logger.

    Arguments:
    loglevel -- a number indicating the level of the logging:
                5 -> logging.CRITICAL
                4 -> logging.ERROR
                3 -> logging.WARNING
                2 -> logging.INFO
                1 -> logging.DEBUG
    """
    # Create logger.
    logger = logging.getLogger(settings.APP_ID)
    logger.setLevel(0 if loglevel not in (5, 4, 3, 2, 1) else loglevel * 10)

    # Create console handler.
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(loglevel)

    # Create formatter and add it to the handler.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handlers to the logger.
    logger.addHandler(handler)

    return logger


def get_logger(name):
    """Return the logger object."""
    return logging.getLogger(settings.APP_ID + "." + name)
