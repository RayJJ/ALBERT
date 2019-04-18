"""
    Program: ALBERT
    Module: abs_events.py

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    version 2 as published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
"""
__author__ = "Ray Jackson"
__copyright__ = "Copyright 2019, Ray Jackson"
__credits__ = []
__license__ = "GNU GPL"
__version__ = "1.0.0"
__maintainer__ = "Ray Jackson"
__email__ = ""
__status__ = "Production"

import abc
from abc import abstractmethod


class AbsUpdatable(metaclass=abc.ABCMeta):

    @abstractmethod
    def on_tick(self):
        """
        interface for all time dependent functions of brain components
        """
        ...

    @abstractmethod
    def on_state_dump(self):
        """
        interface for all state recording functions of brain components
        """
        ...
