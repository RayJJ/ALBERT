"""
User-defined constants, model update functions and model data.
"""

# cells
REST_POTENTIAL = -70
FIRING_POTENTIAL = 0

# spines
MIN_LENGTH = 0.01
MAX_LENGTH = 1.0
CONNECT_LENGTH = 0.94           # microns +/- 0.01 from: Journal of Neurocytology 31, 337–346 (2002)
SPINE_GROWTH_RATE = 1.06
SPINE_DECAY_RATE = 0.99
SPINE_POTENTIAL_DECAY = 0.99    # potential reduces by this factor on each inactive update

# synapses
MIN_STRENGTH = 1
MAX_STRENGTH = 1000
SYNAPSE_GROWTH_RATE = 1.1
SYNAPSE_DECAY_RATE = 0.99
DV_INHIBIT = - 20
DV_EXCITE = -REST_POTENTIAL + 1


# Training values

TRAINING_START_CYCLE = 1                # delay (secs) before training starts
TRAINING_CYCLES = 150
ON = FIRING_POTENTIAL + 1
OFF = REST_POTENTIAL
BIAS_ON = DV_INHIBIT
BIAS_OFF = DV_EXCITE

# model parameters

UPS = 60    # updates per second
DPS = 6     # model data dumps per second


class UserFunctions:

    @staticmethod
    def update_cell(dendrites, injected_potential, firing_threshold):
        potentials = [REST_POTENTIAL, injected_potential]
        for dendrite in dendrites:
            potentials.append(dendrite.potential)
        potential = max(potentials)
        return potential, potential > firing_threshold

    @staticmethod
    def update_dendrite(spines):
        potentials = [REST_POTENTIAL]
        for spine in spines:
            potentials.append(spine.potential)
        return max(potentials)

    @staticmethod
    def update_spine(axon, synapse, length, connected, potential):
        if not connected:
            change_rate = SPINE_GROWTH_RATE if axon.active else SPINE_DECAY_RATE
            length = max(length * change_rate, MIN_LENGTH)
            connected = length >= CONNECT_LENGTH
            potential = REST_POTENTIAL
        else:
            potential = max(SPINE_POTENTIAL_DECAY * (potential - REST_POTENTIAL) + REST_POTENTIAL, synapse.potential)
        return length, connected, potential

    @staticmethod
    def update_synapse(exciter: bool, axon_active: bool, strength: int, bias: float):
        """
        Update synapse strength and potential on each clock tick.

        :param bias:
        :param exciter: type of synapse: True = excitatory, False = inhibitory
        :param axon_active: active state of connected axon: True or False
        :param strength: strength of synapse (proxy for strength of ion channels) [0..MAX_STRENGTH]
        :return: strength [0..MAX_STRENGTH], potential [mV]
        """
        if axon_active:
            strength = min(strength * SYNAPSE_GROWTH_RATE, MAX_STRENGTH)
            dv = DV_EXCITE if exciter else DV_INHIBIT
            norm_strength = strength / MAX_STRENGTH
            potential = dv * norm_strength + REST_POTENTIAL
        else:
            strength = max(strength * SYNAPSE_DECAY_RATE, MIN_STRENGTH)
            potential = REST_POTENTIAL
        # potential += bias
        return strength, potential

    @staticmethod
    def update_node(cells, dendrites, spines):
        # node potential = max potentials of local cells
        return max([REST_POTENTIAL] + [cell.potential for cell in cells.values()] +
                   [dendrite.potential for dendrite in dendrites] +
                   [REST_POTENTIAL + spine.synapse.potential for spine in spines if spine.connected])

training_data = {
    'md-01': {
        'cell_keys': ['bias', 'se-01', 'se-07'],
        'values': [
            # alternate wrong - right answers with bias to give confirmation for learning
            [BIAS_ON, ON, ON],
            [BIAS_OFF, ON, OFF],
            [BIAS_OFF, OFF, ON],
            [BIAS_ON, OFF, OFF],
        ]
    },
    'md-02': {
        'cell_keys': ['bias', 'se-16', 'se-22'],
        'values': [
            # alternate wrong - right answers with bias to give confirmation for learning
            [BIAS_ON, ON, ON],
            [BIAS_OFF, ON, OFF],
            [BIAS_OFF, OFF, ON],
            [BIAS_ON, OFF, OFF],
        ]
    },
}

cell_types = {
        "sensor": {  # cell type
            "firing_threshold": FIRING_POTENTIAL,  # potential threshold
            "axons": {
                "1": {
                    "exciter": True,
                    "relative_locs": [(1, 0)]
                }
            }
        },
        "pyramid": {  # cell type
            "firing_threshold": FIRING_POTENTIAL,  # potential threshold
            "axons": {
                "1": {  # inhibitory axon
                    "exciter": False,
                    "relative_locs": [(0, -1), (1, -1)]
                },
                "2": {  # excitatory axon
                    "exciter": True,
                    "relative_locs": [(1, 0)]
                },
                "3": {  # inhibitory axon
                    "exciter": False,
                    "relative_locs": [(0, 1), (1, 1)]
                },
            },
            "dendrites": {
                "1": {
                    "spine_growth": SPINE_GROWTH_RATE,  # strength growth / active update cycle
                    "spine_decay": SPINE_DECAY_RATE,  # strength growth / active update cycle
                    "connect_threshold": CONNECT_LENGTH,  # strength threshold for connection
                    "relative_locs": [(-1, -1), (-2, -1)],
                },
                "2": {
                    "spine_growth": SPINE_GROWTH_RATE,  # strength growth / active update cycle
                    "spine_decay": SPINE_DECAY_RATE,  # strength growth / active update cycle
                    "connect_threshold": CONNECT_LENGTH,  # strength threshold for connection
                    "relative_locs": [(-1, 0), (-2, 0)],
                },
                "3": {
                    "spine_growth": SPINE_GROWTH_RATE,  # strength growth / active update cycle
                    "spine_decay": SPINE_DECAY_RATE,  # strength growth / active update cycle
                    "connect_threshold": CONNECT_LENGTH,  # strength threshold for connection
                    "relative_locs": [(-1, 1), (-2, 1)]
                }
            }
        },
        "motor": {  # cell type
            "firing_threshold": FIRING_POTENTIAL,  # potential threshold
            "dendrites": {
                "1": {
                    "spine_growth": SPINE_GROWTH_RATE,  # strength growth / active update cycle
                    "spine_decay": SPINE_DECAY_RATE,  # strength growth / active update cycle
                    "connect_threshold": CONNECT_LENGTH,  # strength threshold for connection
                    "relative_locs": [(-1, 0), (-2, 0)]
                }
            }
        },
}  # end cell_types

brain = {  # start brain
    "description": "Learning Trials.",
    "modules": [
        # 0: {
        #     "description": "Simple 1-neuron 1-sensor module",
        #     "dimensions": (10, 10),
        #         "sensor": {  # instantiate dictionary with locations as keys
        #             "locations": [(0, 2)]  # auto-label n1..n5 etc
        #         },
        #         "pyramid": {  # instantiate dictionary with locations as keys
        #             "locations": [(3, 2)]  # auto-label s1..s2 etc
        #         },
        #         "motor": {  # instantiate dictionary with locations as keys
        #             "locations": [(7, 2)]  # auto-label m1..m2 etc
        #         },
        # },  # end module-0
        {
            "description": "A 3-layer, 6-neuron module",
            "dimensions": (9, 9),
            "cells": {
                "sensor": {  # instantiate dictionary with locations as keys
                    "locations": [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]  # auto-label 1..n
                },
                "pyramid": {  # instantiate dictionary with locations as keys
                    "locations": [(2, 2), (2, 4), (2, 6), (4, 3), (4, 5), (6, 4)]  # auto-label 1..n
                },
                "motor": {  # instantiate dictionary with locations as keys
                    "locations": [(8, 4)]  # auto-label 1..n
                },
            },
        },  # end module-1
        # {
        #     "description": "A 2-layer, 7-neuron module",
        #     "dimensions": (7, 11),
        #     "cells": {
        #         "sensor": {
        #             "locations": [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
        #         },
        #         "pyramid": {
        #             "locations": [(2, 2), (2, 4), (2, 6), (2, 8), (4, 3), (4, 5), (4, 7)]
        #         },
        #         "motor": {
        #             "locations": [(6, 3), (6, 5), (6, 7)]
        #         },
        #     },
        # }  # end module-2
    ],  # end modules
    # "bridges": [  # instantiate dictionary in each module with locations as keys
    #     {
    #         "from": (1, (3, 2)),
    #         "to": (1, (5, 4))
    #     },
        # {
        #     "from": ("module-1", (3, 6)),
        #     "to": ("module-1", (5, 4))
        # },
        # {
        #     "from": (1, (5, 5)),
        #     "to": (2, (1, 2))
        # },
    # ]  # end bridges
}  # end brains

# plots requested

plot_request = [
    {'type': 'figure', 'title': 'ALBERT Test Model'},
    {'type': 'cell-map', 'sub-plot': (1, 1), 'module': 'md-01'},
    {'type': 'heatmap',  'sub-plot': (1, 2), 'module': 'md-01', 'variable': 'potential'},
    {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-01', 'variable': 'length',
     'items': 'spines',  'item-keys': ['sp-01', 'sp-05', 'sp-17']},
    {'type': 'lines',    'sub-plot': (2, 2), 'module': 'md-01', 'variable': 'potential',
     'items': 'synapses', 'item-keys': ['sy-01', 'sy-05', 'sy-17']},
    {'type': 'lines',    'sub-plot': (2, 3), 'module': 'md-01', 'variable': 'potential',
     'items': 'dendrites',  'item-keys': ['de-01', 'de-10', 'de-16']},
    {'type': 'lines',    'sub-plot': (1, 3), 'module': 'md-01', 'variable': 'potential',
     'items': 'cells', 'item-keys': ['ne-08', 'ne-11', 'ne-13']},
    # {'type': 'cell-map', 'sub-plot': (1, 1), 'module': 'md-02'},
    # {'type': 'heatmap',  'sub-plot': (1, 2), 'module': 'md-02', 'variable': 'potential'},
    # {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-02', 'variable': 'potential',
    #  'items': 'cells', 'item-keys': ['se-16']},
    # {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-01', 'variable': 'potential',
    #  'items': 'dendrites',  'item-keys': ['de-08', 'de-11', 'de-14']},
    # {'type': 'lines',    'sub-plot': (2, 2), 'module': 'md-01', 'variable': 'potential',
    #  'items': 'cells',  'item-keys': ['mo-14']}
]
