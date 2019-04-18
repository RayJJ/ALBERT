"""
    Program: ALBERT
    Module: spine.py

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

import itertools
from abs_events import AbsUpdatable
from constants import *
from synapse import Synapse
from model_spec import UserFunctions, SPINE_GROWTH_RATE, SPINE_DECAY_RATE, REST_POTENTIAL, CONNECT_LENGTH


class Spine(AbsUpdatable):
    """
    Spines connect dendrites to axons.
    Spines exist for every axon-dendrite pair within a node but initially have zero length (ie they are unconnected.

    Spines grow and shrink, and consequently connect and disconnect dendrite-axon pairs within a node of a module.
    They cannot disconnect if where a synapse has remaining strength.

    Spine updates are requested by their dendrites.

    Limitations: A feeder axon is either excitatory or inhibitory, therefore individual spines
                 build either an excitatory or inhibitory potential, but not a mix.
    """
    spine_count = 0
    _spine_counter = itertools.count(1)

    def __init__(self, module, location: tuple, dendrite, axon):
        # keep count of created objects
        Spine.spine_count = next(self._spine_counter)
        # spine has:
        self.key = f'sp-{Spine.spine_count:02d}'
        self.module = module
        self.location = location
        self.dendrite = dendrite  # parent dendrite for this spine
        self.axon = axon  # axon feeding this spine
        self.connect_length = CONNECT_LENGTH  # length required to connect to nearby axon
        self.length = 0  # initial strength of spine
        self.potential = REST_POTENTIAL  # log(synapse.strength) if length > THRESHOLD else 0
        self.connected = False  # connected to axon?
        self.synapse = Synapse(self.module, self.location, self, self.axon,
                               1 if self.axon.exciter else -1)  # only one synapse per spine

    def on_state_dump(self):
        return {
            KEY: self.key,
            CELL_TYPE: SPINE,
            MODULE: self.module.key,
            LOCATION: self.location,
            DENDRITE: self.dendrite.key,
            AXON: self.axon.key,
            CONNECTED: self.connected,  # once connected, stays connected
            POTENTIAL: self.potential,
            SPINE_LENGTH: self.length,
            SYNAPSE: self.synapse.key,
        }

    def on_tick(self):
        if self.connected:
            self.synapse.on_tick()
        self.length, self.connected, self.potential = \
            UserFunctions.update_spine(self.axon, self.synapse, self.length, self.connected, self.potential)

    def __repr__(self):
        return \
            f"\t\t Spine: {self.location}" + \
            f" Axon {self.axon.key}" + \
            f" Dendrite {self.dendrite.key}" + \
            f" Pd {self.potential} mV"
