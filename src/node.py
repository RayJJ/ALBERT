from abs_events import AbsUpdatable
from spine import Spine
import itertools

from model_spec import UserFunctions, REST_POTENTIAL
from constants import *


class Node(AbsUpdatable):

    count = 0
    _counter = itertools.count(1)

    def __init__(self, location, module):
        # keep count of created objects
        Node.count = next(self._counter)
        # a node belongs to:
        self.module = module
        # a node has:
        self.location = location
        self.potential = REST_POTENTIAL
        # a node contains:
        self.cells = {}
        self.axons = []
        self.dendrites = []
        self.spines = []

    def on_state_dump(self):
        return {
            LOCATION: self.location,
            POTENTIAL: self.potential,
            CELLS: [key for key in self.cells.keys()],
            DENDRITES: [dendrite.key for dendrite in self.dendrites],
            SPINES: [spine.key for spine in self.spines],
            AXONS: [axon.key for axon in self.axons],
        }

    def on_content_request(self) -> []:
        """
        represent the contents of this node with a list of unique component references
        :return: list of component references e.g. ['n3', 'd11', 'd12', 'a2']
        """
        return [self.location] + [f'{cell.key}' for cell in self.cells.values()] + \
            [f'{dendrite.key}' for dendrite in self.dendrites] + \
            [f'{spine.key}' for spine in self.spines] + \
            [f'{spine.synapse.key}' for spine in self.spines] + \
            [f'{axon.key}' for axon in self.axons]

    def on_tick(self):
        self.potential = UserFunctions.update_node(self.cells, self.dendrites, self.spines)

    def connect(self):
        # at this node, each dendrite can connect to each axon via a connecting spine
        for dendrite in self.dendrites:
            for axon in self.axons:
                # skip connections between axons and dendrites from the same soma (gives uncontrolled feedback)
                if dendrite.parent == axon.parent:
                    continue
                spine = Spine(self.module, self.location, dendrite, axon)
                self.spines.append(spine)
                dendrite.spines.append(spine)
                # connect axon parent cell (parent) to dendrite parent cell (child)
                axon.parent.children.add(dendrite.parent)

    def __repr__(self):
        return "C:" + str(self.location)\
               + " A:" + str(self.axons) \
               + " D:" + str(self.dendrites) \
               + " s:" + str(self.spines)
