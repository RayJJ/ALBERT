"""
    Program: ALBERT
    Module: actor.py

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

from model_spec import DPS, UPS
from utils import timed_call
from brain import Brain
from constants import *
import time
import logging
import cProfile


class Actor:
    """
    Actor is a container for a Brain.
    The Actor.live() function brings the actor to life.

    """

    def __init__(self, pipe, brain, cell_types, updates_per_second=60, trainer=None, monitor=None, profiling=False):

        self.profiling = profiling
        if profiling:
            self.profiler = cProfile.Profile()
            self.profiler.disable()

        # pipe to receive requests and send data
        self.pipe = pipe

        # brain state
        self.brain = Brain(self, brain, cell_types)
        self.trainer = trainer
        self.trainer.brain = self.brain
        self.monitor = monitor
        self.updates_per_second = updates_per_second
        self.alive = False
        self.time_alive = 0
        self.state = None

        # node_contents = [module.on_content_request() for module in self.brain.modules]
        # logging.info(pformat(node_contents, compact=False, width=600))

    def stop_profiling(self):
        if self.profiling:
            # stop profiling
            self.profiler.disable()
            # print profile results
            logging.info(self.profiler.print_stats(sort="cumulative"))

    def _die(self):
        self.stop_profiling()
        # stop main loop in live()
        self.alive = False

    def live(self):

        self.alive = True
        paused = False

        # calc time per cycle through the model
        time_per_cycle = NS / self.updates_per_second
        logging.info(f"cycle time  =\t{time_per_cycle / NS_PER_MS: 8.2f} ms")

        if self.profiling:
            # start profiling
            self.profiler.enable()

        while self.alive:

            # check for user commands
            if self.pipe.poll():
                message = self.pipe.recv()
                if message == DIE:
                    logging.info('***** "die" message received. *****')
                    self._die()
                    break
                elif message == PAUSE:
                    if paused:
                        logging.info('***** "un-pause" message received. *****')
                    else:
                        logging.info('***** "pause" message received. *****')
                    paused = not paused

            if paused:
                # print('paused\n')
                continue

            #  zero times of operations
            time_for_brain = 0
            time_for_sleep = 0
            time_for_sensors = 0
            time_for_state_dump = 0

            for update in range(self.updates_per_second):

                #  first cycle: update sensors
                if update == 0 and self.trainer is not None:
                    time_for_sensors += timed_call(self.trainer.on_tick)

                #  all cycles: update brain
                t_brain = timed_call(self.brain.on_tick)
                time_for_brain += t_brain

                # last cycle: send brain state to monitor
                t_state_dump = 0
                if update % (UPS / DPS) == 0:
                    t_state_dump = timed_call(self._send_state_to_monitor, delta_t=time_per_cycle)
                    time_for_state_dump += t_state_dump

                # wait for end of cycle
                time_left_in_cycle = time_per_cycle - t_brain - t_state_dump
                if time_left_in_cycle > 0:
                    time.sleep(time_left_in_cycle / NS)
                else:
                    logging.warning(f"Warning: cycle overrun: time left = {time_left_in_cycle / NS_PER_MS}")

                time_for_sleep += time_left_in_cycle
                # time alive measured in cycles (= seconds * UPS)
                self.time_alive += 1

            # log times
            logging.info(f"sensor time =\t{time_for_sensors / NS_PER_MS: 8.2f} ms")
            logging.info(f"brain time  =\t{time_for_brain / NS_PER_MS: 8.2f} ms")
            logging.info(f"sleep time  =\t{time_for_sleep / NS_PER_MS: 8.2f} ms")
            logging.info(f"log time    =\t{time_for_state_dump / NS_PER_MS: 8.2f} ms")

    def _send_state_to_monitor(self, delta_t):

        self.state = self.brain.on_state_dump()
        self.state[TIME_ALIVE_CYCLES] = self.time_alive
        # logging.info('++++++++++++ STATE ++++++++++++')
        # logging.info(pformat(self.state, compact=False, width=600))
        # logging.info('++++++++++++ STATE ++++++++++++')
        self.pipe.send(self.state)
