"""
    Program: ALBERT
    Module: main.py

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

from multiprocessing import Pipe, Process
import logging
# app modules
from monitor import Monitor
from actor import Actor
from trainer import Trainer
from model_spec import UPS, cell_types, brain, plot_request

# main process...
if __name__ == "__main__":

    # log to file
    logging.basicConfig(level=logging.INFO,
                        filename='app.log',
                        filemode='w',
                        format='%(message)s\t\t')
    # make monitor<=>actor pipe
    monitor_connection, actor_connection = Pipe()
    # make trainer to feed inputs to actor's brain
    trainer = Trainer(randomise=False)
    # make monitor
    monitor = Monitor(monitor_connection, plot_request, profiling=False)
    # make actor
    actor = Actor(actor_connection, brain, cell_types, UPS, trainer, monitor, profiling=False)
    # start actor in separate process
    Process(target=actor.live, args=()).start()
    # start monitor
    monitor.start()
