from operator import add
import itertools

from abs_events import AbsUpdatable
from model_spec import UserFunctions, REST_POTENTIAL, FIRING_POTENTIAL
from constants import *


class Dendrite(AbsUpdatable):
    """ Dendrite class creates dendrites from the specifications in models.py. """

    dendrite_count = 0
    _dendrite_counter = itertools.count(1)

    def __init__(self, parent, dendrite_spec):
        # keep count of created objects
        Dendrite.dendrite_count = next(Dendrite._dendrite_counter)
        #
        self.key = f'de-{Dendrite.dendrite_count:02d}'
        self.parent = parent
        self.spines = []        # spines (initially zero length and unconnected) at all nodal axon-dendrite junctions
        self.locations = [parent.location] + \
                         [tuple(map(add, loc, parent.location)) for loc in dendrite_spec['relative_locs']]
        self.potential = REST_POTENTIAL

    def on_state_dump(self):
        return {
            KEY: self.key,
            CELL_TYPE: DENDRITE,
            LOCATIONS: self.locations,
            POTENTIAL: self.potential,
            # ACTIVE: self.parent.active and self.potential >= FIRING_POTENTIAL,
            ACTIVE: self.potential >= FIRING_POTENTIAL,
            SPINES: [spine.key for spine in self.spines],
        }

    def on_tick(self):
        for spine in self.spines:
            spine.on_tick()
        self.potential = UserFunctions.update_dendrite(self.spines)
