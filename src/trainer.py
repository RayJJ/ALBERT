import random
import logging

from model_spec import training_data, BIAS_ON, TRAINING_START_CYCLE, TRAINING_CYCLES


class Trainer:

    def __init__(self, randomise=False):

        random.seed(123456789)
        self.randomise = randomise
        self.brain = None
        self.data_row = {}
        self.cycle = 0

    def on_tick(self):

        # update is called by actor once per second

        self.cycle += 1

        if self.cycle <= TRAINING_START_CYCLE:
            return

        logging.info(f"Cycle {self.cycle:2}")

        for module in self.brain.modules:

            if module.key in training_data:

                # initialise the row counter for this module
                if module.key not in self.data_row:
                    self.data_row[module.key] = 0

                # set bias for training / non-training cycles in this module
                if self.cycle < TRAINING_CYCLES:
                    # bias is feedback when learning; ON = wrong, OFF = right
                    module.bias = training_data[module.key]['values'][self.data_row[module.key]][0]
                else:
                    # bias defaults to ON when not learning
                    module.bias = BIAS_ON

                # set sensor values
                cell = 1
                for cell_key in training_data[module.key]['cell_keys']:
                    if cell_key in module.cells.keys():
                        module.cells[cell_key].injected_potential = \
                            training_data[module.key]['values'][self.data_row[module.key]][cell]
                        cell += 1

                # select the next data row
                if self.randomise:
                    self.data_row[module.key] = random.randint(0, len(training_data[module.key]['values']) - 1)
                else:
                    # cycle through the set of data values
                    self.data_row[module.key] = \
                        (self.data_row[module.key] + 1) % len(training_data[module.key]['values'])
