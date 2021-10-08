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

from gi.repository import GLib


class ProcessView:
    """Utility class for layouts to do async tasks.

    The requirements are the following:
    - It needs a callback that receives an argument.
    - It needs a function and arguments in a tuple.
    """

    def __init__(self, cb, func, tuple_args):
        """
        Arguments:
        cb         -- callback that will receive an argument.
        func       -- the function that will be execute async (in a multiprocessing.Process).
        tuple_args -- tuple with all arguments that func receives.
        """
        self._cb = cb
        self._func = func
        self._args = tuple_args

    def start(self):
        thread = threading.Thread(target=self._run)
        thread.start()

    def _run(self):
        if self._args:
            result = self._func(*self._args)
        else:
            result = self._func()
        GLib.idle_add(self._cb, result)
