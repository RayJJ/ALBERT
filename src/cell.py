from abs_events import AbsUpdatable
from model_spec import UserFunctions, REST_POTENTIAL
from axon import Axon
from dendrite import Dendrite
from constants import *
import itertools


class Cell(AbsUpdatable):
    """
    A cell can have any number of axons and/or dendrites. These may cross nodes in a module that contain complimentary
    Axons or Dendrites. Complimentary components in the same node of a module can connect by growing connecting spines
    and then strengthening the link (synapse) between them.

    These components can extend over any number of locations in a module.

    A module can span two or three dimensions and can be connected to other modules by Bridges.
    """

    cell_count = 0
    _cell_counter = itertools.count(1)

    def __init__(self, module, location, spec):
        # keep count of created objects
        Cell.cell_count = next(Cell._cell_counter)
        #
        self.module = module
        self.location = location
        self.children = set([])
        self.firing_threshold = spec[FIRING_THRESHOLD]
        self.active = False
        self.injected_potential = REST_POTENTIAL
        self.potential = REST_POTENTIAL
        self.axons = self._make_axons(spec)
        self.dendrites = self._make_dendrites(spec)
        self.cell_type = self._get_cell_type()
        self.key = f'{self.cell_type[:2]}-{Cell.cell_count:02d}'

    def _make_dendrites(self, spec):
        if DENDRITES in spec.keys():
            return [Dendrite(self, dendrite_spec) for dendrite_spec in spec[DENDRITES].values()]
        else:
            return []

    def _make_axons(self, spec):
        if AXONS in spec.keys():
            return [Axon(self, axon_spec) for axon_spec in spec[AXONS].values()]
        else:
            return []

    def _get_cell_type(self):
        if self.dendrites:
            return NEURON if self.axons else MOTOR
        else:
            return SENSOR if self.axons else SOMA

    def on_state_dump(self):
        return {
            KEY: self.key,
            CELL_TYPE: self.cell_type,
            MODULE: self.module.key,
            LOCATION: self.location,
            INJECTED_POTENTIAL: self.injected_potential,
            POTENTIAL: self.potential,
            FIRING_THRESHOLD: self.firing_threshold,
            ACTIVE: self.active,
            CHILDREN: [cell.key for cell in self.children],
            AXONS: [axon.key for axon in self.axons],
            DENDRITES: [dendrite.key for dendrite in self.dendrites],
        }

    def on_tick(self):

        # update order: dendrites - soma - axons

        for dendrite in self.dendrites:
            dendrite.on_tick()
        self.potential, self.active = UserFunctions.update_cell(
            self.dendrites, self.injected_potential, self.firing_threshold)
        for axon in self.axons:
            axon.on_tick()
