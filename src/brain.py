"""
    Program: ALBERT
    Module: brain.py

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

import logging

from abs_events import AbsUpdatable
from module import Module
from bridge import Bridge
from constants import *


# noinspection PyBroadException
class Brain(AbsUpdatable):

    def __init__(self, actor, brain, cell_types):
        # the actor hosting this brain
        self.actor = actor
        # the brain has:
        self.description = brain[DESCRIPTION]
        self.module_specs = None
        self.modules = []
        self.bridge_specs = None
        self.bridges = []
        # cell and module specifications
        self.cell_specs = cell_types
        if 'modules' in brain.keys():
            self.module_specs = brain[MODULES]
        else:
            logging.warning(f"*** Warning: No modules in model for brain")
        if 'bridges' in brain.keys():
            self.bridge_specs = brain["bridges"]
        else:
            logging.warning(f"*** Warning: No bridges in model for brain")
        # create modules from available specs
        if self.module_specs is not None:
            for module_spec in self.module_specs:
                self.modules.append(Module(self, module_spec, self.cell_specs))
        # create bridges from available specs
        if self.bridge_specs is not None:
            for bridge_spec in self.bridge_specs:
                self.bridges.append(Bridge(self, bridge_spec))
        # report brain metrics
        for module in self.modules:
            logging.info(f'\nmodule: {module.key}:' +
                         f'\n\t{len(module.cells)} ' + CELLS +
                         f'\n\t{len(module.axons)} ' + AXONS +
                         f'\n\t{len(module.dendrites)} ' + DENDRITES +
                         f'\n\t{sum([len(node.spines) for node in module.nodes.values()])} nascent ' + SPINES
                         )
        logging.info(f'\nbridges: {len(self.bridges)}')

    def on_state_dump(self):
        return {
            DESCRIPTION: self.description,
            MODULES: {list(module.on_state_dump().keys())[0]: list(module.on_state_dump().values())[0] for module in self.modules},
            BRIDGES: {bridge.key: bridge.on_state_dump() for bridge in self.bridges},
        }

    def on_tick(self):
        for module in self.modules:
            module.on_tick()
        # note: bridges are updated within the modules that they connect.
