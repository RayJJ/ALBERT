"""
    Program: ALBERT
    Module: synapse.py

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
import itertools
from constants import *
from model_spec import UserFunctions, SYNAPSE_GROWTH_RATE, SYNAPSE_DECAY_RATE, MIN_STRENGTH, REST_POTENTIAL


class Synapse(AbsUpdatable):
    """
    A synapse is a direct connection between a spine and an axon. It only exists when a spine and an axon are connected.
    Spines and axons can connect where they occupy the same node of a module.
    Axon-Spine pairs may thus share several synapses.
    """
    synapse_count = 0
    _synapse_counter = itertools.count(1)

    def __init__(self, module, location: tuple, spine, axon, excite: int):
        # keep count of created objects
        Synapse.synapse_count = next(self._synapse_counter)
        #
        self.key = f'sy-{Synapse.synapse_count:02d}'  # who ami I?
        self.module = module                # where am I? (roughly)
        self.location = location            # where am I? (precisely) = module.nodes[location]
        self.axon = axon                    # axon feeding this synapse
        self.spine = spine                  # parent dendritic spine for this synapse
        self.strength = MIN_STRENGTH        # initial strength of synapse
        self.potential = REST_POTENTIAL

    def on_state_dump(self):
        return {
            KEY: self.key,
            CELL_TYPE: SYNAPSE,
            MODULE: self.module.key,
            LOCATION: self.location,
            AXON: self.axon.key,
            SPINE: self.spine.key,
            EXCITER: self.axon.exciter,
            STRENGTH: self.strength,
            POTENTIAL: self.potential,
        }

    def on_tick(self):
        self.strength, self.potential = UserFunctions.update_synapse(
            self.axon.exciter, self.axon.active, self.strength, self.module.bias)

    def __repr__(self):
        return \
            f"\t\t Synapse: {self.location}" + \
            f" Axon {self.axon.key}" + \
            f" Dendrite {self.spine.dendrite.key}" + \
            f" Spine {self.spine.key}" + \
            f" Strength {self.strength}" + \
            f" Pd {self.potential} mV"
