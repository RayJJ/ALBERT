"""
    Program: ALBERT
    Module: module.py

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
import itertools

from abs_events import AbsUpdatable
from cell import Cell

from node import Node
from constants import *


# noinspection PyBroadException
from model_spec import REST_POTENTIAL, DV_INHIBIT


class Module(AbsUpdatable):

    module_count = 0
    _module_counter = itertools.count(1)

    def __init__(self, brain, module_spec, cell_specs):
        """
        A 2D or 3D collection of nodes providing the spatial scaffolding for cells and bridges.
        """
        # keep count of created objects
        Module.module_count = next(self._module_counter)
        # keep reference to host brain
        self.brain = brain
        # module state
        self.key = f'md-{Module.module_count:02d}'
        self.description = module_spec[DESCRIPTION]
        self.dimensions = module_spec[DIMENSIONS]  # dimensions
        self.bias = REST_POTENTIAL + DV_INHIBIT
        self.cells = {}
        self.axons = []
        self.dendrites = []
        self.spines = []
        self.synapses = []
        self.nodes = {}  # dictionary of nodes referenced by location tuples
        # populate the nodes
        self._create_nodes()
        # create cells
        try:
            for cell_type, cell_spec in module_spec[CELLS].items():
                self.make_cells(cell_type, cell_spec, cell_specs)
        except:
            logging.warning(f"*** Warning: No cells in model: {self.key}")
        # create spines to connect axons and dendrites in each node
        for node in self.nodes.values():
            node.connect()

    def on_state_dump(self):
        return {
            self.key: {
                DESCRIPTION: self.description,
                DIMENSIONS: self.dimensions,
                BIAS: self.bias,
                CELLS: {key: cell.on_state_dump() for key, cell in self.cells.items()},
                AXONS: {axon.key: axon.on_state_dump() for axon in self.axons},
                DENDRITES: {dendrite.key: dendrite.on_state_dump() for dendrite in self.dendrites},
                SPINES: {spine.key: spine.on_state_dump() for dendrite in self.dendrites for spine in dendrite.spines},
                SYNAPSES: {spine.synapse.key: spine.synapse.on_state_dump() for dendrite in self.dendrites for spine in dendrite.spines},
                NODES: {key: node.on_state_dump() for key, node in self.nodes.items()},
            }
        }

    def on_content_request(self):
        return [str(self.key)] + [
            node.on_content_request() for node in self.nodes.values() if len(node.on_content_request()) > 1
        ]

    def make_cells(self, cell_type, cell_spec, cell_specs):
        for location in cell_spec[LOCATIONS]:
            cell = Cell(self, location, cell_specs[cell_type])
            self.cells[cell.key] = cell
            self.nodes[location].cells[cell.key] = cell
            # reference dendrites from the nodes that they cross
            self.add_dendrites_to_nodes(cell)
            # reference axons from the nodes that they cross
            self.add_axons_to_nodes(cell)

    def add_axons_to_nodes(self, cell):
        for axon in cell.axons:
            self.axons.append(axon)
            for loc in axon.locations:
                self.nodes[loc].axons.append(axon)

    def add_dendrites_to_nodes(self, cell):
        for dendrite in cell.dendrites:
            self.dendrites.append(dendrite)
            for spine in dendrite.spines:
                self.spines.append(spine)
            for location in dendrite.locations:
                self.nodes[location].dendrites.append(dendrite)

    def on_tick(self):
        cell_set = set([])
        cells_done = set([])
        cell_next_set = set([])
        # starting with sensors, activate cell network in breadth-first order
        for cell in self.cells.values():
            if cell.cell_type == SENSOR:
                cell_set.add(cell)
        while len(cell_set) > 0:
            # update this layer
            for cell in cell_set:
                # avoid infinite loop if cells feedback into network
                # feedback is incorporated in next pass through the network
                if cell not in cells_done:
                    cell.on_tick()
                    cells_done.add(cell)
                # add child cells to next_set
                for child in cell.children:
                    cell_next_set.add(child)
            # set up for next layer
            cell_set = cell_next_set
            cell_next_set = set([])
        # update nodes
        self.nodes_on_tick()

    def nodes_on_tick(self):
        dims = len(self.dimensions)
        if dims == 2:
            for row in range(self.dimensions[0]):
                for col in range(self.dimensions[1]):
                    self.nodes[(row, col)].on_tick()
        elif dims == 3:
            for row in range(self.dimensions[0]):
                for col in range(self.dimensions[1]):
                    for layer in range(self.dimensions[2]):
                        self.nodes[(row, col, layer)].on_tick()
        else:
            raise ValueError("%s dimensions provided. Only 2 and 3 dimensions are supported." % dims)

    def _create_nodes(self):
        dims = len(self.dimensions)
        if dims == 2:
            self.nodes = {(i, j): Node((i, j), self)
                          for j in range(self.dimensions[1])
                          for i in range(self.dimensions[0])}
        elif dims == 3:
            self.nodes = {(i, j, k): Node((i, j, k), self)
                          for k in range(self.dimensions[2])
                          for j in range(self.dimensions[1])
                          for i in range(self.dimensions[0])}
        else:
            raise ValueError("%s dimensions provided. Only 2 and 3 dimensions are supported." % dims)
