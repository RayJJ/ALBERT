from spine import Spine
import itertools
from abs_events import AbsUpdatable

from constants import *


class Bridge(AbsUpdatable):
    """
    Bridge creates a bridge from the specifications in models.py. It acts like a 'long-range' synapse.
    A bridge creates spines on all dendrites in the destination node that connect to all axons in the source node.
    """

    bridge_count = 0
    _bridge_counter = itertools.count(1)

    def __init__(self, brain, bridge_spec):
        # keep count of created objects
        Bridge.bridge_count = next(self._bridge_counter)
        # reference to host brain
        self.brain = brain
        # a bridge contains:
        self.axon = None
        self.dendrite = None
        # a bridge has:
        self.key = Bridge.bridge_count
        self.from_module_id = bridge_spec["from"][0]
        self.from_location = bridge_spec["from"][1]
        self.to_module_id = bridge_spec["to"][0]
        self.to_location = bridge_spec["to"][1]
        self.active = False
        # create spines to connect each end of the bridge to co-located cells
        self._connect()

    def on_state_dump(self):
        if self.axon is None or self.dendrite is None:
            return {
                KEY: self.key,
                FROM_LOCATION: self.from_location,
                TO_LOCATION: self.to_location,
                FROM_MODULE_ID: self.from_module_id,
                TO_MODULE_ID: self.to_module_id,
                ACTIVE: self.active,
                AXON: 'None',
                DENDRITE: 'None',
            }
        else:
            return {
                FROM_LOCATION: self.from_location,
                TO_LOCATION: self.to_location,
                FROM_MODULE_ID: self.from_module_id,
                TO_MODULE_ID: self.to_module_id,
                ACTIVE: self.active,
                AXON: self.axon.on_state_dump(),
                DENDRITE: self.dendrite.on_state_dump(),
            }

    def on_tick(self):
        # receiving dendrites trigger updates to spine / synapse for the bridge
        pass

    def _connect(self):
        """ create spines to connect each end of the bridge to co-located cells """
        # get module(s) from brain
        from_module = [module for module in self.brain.modules if module.key == self.from_module_id][0]
        to_module = [module for module in self.brain.modules if module.key == self.to_module_id][0]
        # get from and to nodes from relevant modules
        from_node = from_module.nodes[self.from_location]
        to_node = to_module.nodes[self.to_location]
        # connect each axon in source node to each dendrite in destination node
        for dendrite in to_node.dendrites:
            for axon in from_node.axons:
                spine = Spine(to_module.key, to_node.location, axon, dendrite)
                dendrite.spines.append(spine)
        # ToDo: test and debug bridge update process
