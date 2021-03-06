"""
    Program: ALBERT
    Module: axon.py

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

from abs_events import AbsUpdatable
from operator import add
import itertools
from constants import *


class Axon(AbsUpdatable):

    axon_count = 0
    _axon_counter = itertools.count(1)

    def __init__(self, parent, axon_spec):
        """
        Axon class creates axons from the specifications in models.py.
        """
        # keep count of created objects
        Axon.axon_count = next(Axon._axon_counter)
        # parent cell
        self.parent = parent
        # key is unique for all axons
        self.key = f'ax-{Axon.axon_count:02d}'
        # calculate absolute locations of host nodes in the module
        # element-wise addition of location tuples
        self.locations = [parent.location] + \
                         [tuple(map(add, loc, parent.location)) for loc in axon_spec['relative_locs']]
        self.exciter = axon_spec[EXCITER]
        self.active = False

    def on_state_dump(self):
        return {
            KEY: self.key,
            CELL_TYPE: AXON,
            LOCATIONS: self.locations,
            EXCITER: self.exciter,
            ACTIVE: self.active,
        }

    def on_tick(self):
        self.active = self.parent.active
