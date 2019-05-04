"""
    Program: ALBERT
    Module: monitor.py

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
import time
import cProfile
from pprint import pformat as pformat
# app modules
import utils
from model_spec import DPS

from plotter import Plotter
from translator import DataTranslator
from constants import NS_PER_MS


class Monitor:

    def __init__(self, pipe, required_plots: list, profiling=False):

        self.profiling = profiling
        if profiling:
            self.pr = cProfile.Profile()
            self.pr.disable()
        # a monitor has:
        # pipe to send requests and receive data from the brain model
        self.pipe = pipe
        # required plots for each module
        self.required_plots = required_plots
        # model state
        self.data_batch = 0
        self.plot_time = 0
        self.model_data = None
        self.plotter = None
        self.monitoring = True
        self.started = False
        self.logged_plot_data = False
        self.paused = False

    def start(self):
        logging.info("*** Starting monitor...")
        if self.profiling:
            # start profiling
            self.pr.enable()
        # poll pipe for data and update plots until window is closed
        while self.monitoring:
            if self.paused:
                # draw flushes ui events ensuring key press events are handled
                self.plotter.draw()
                continue
            if self.pipe.poll():  # true when data available
                self.process_data()

    def _end_app(self, event):
        # stop actor's process
        self.pipe.send('die')
        if self.profiling:
            time.sleep(0.2)
            # stop profiling
            self.pr.disable()
            # print profile results
            logging.info(self.pr.print_stats(sort="calls"))
        self.monitoring = False

    def _pause_app(self, event):
        if event.key == 'enter':
            # pause / un-pause the monitor
            self.paused = not self.paused
            # pause / un-pause the model
            self.pipe.send('pause')
            self.plotter.show_state(self.paused)

    def process_data(self):
        model_state = self.pipe.recv()
        self.process_model_data(model_state)

    def process_model_data(self, model_state: {}):
        self.data_batch += 1
        figure_data, plot_data = self.translate_data(model_state)
        self._log_once(plot_data)
        self.plot_time += utils.timed_call(self.plot_it, figure_data=figure_data, plot_data=plot_data) / NS_PER_MS
        if self.data_batch % DPS == 0:
            logging.info(f"plot time   =\t{self.plot_time: 8.2f} ms")
            self.plot_time = 0

    def _log_once(self, plot_data):
        if not self.logged_plot_data:
            logging.info('\nFirst plot_data file: \n' +
                         '(include a cellmap in the plot_request to see keys and relations' +
                         ' for all cell component data)\n\n')
            logging.info(pformat(plot_data, compact=False, width=600))
            self.logged_plot_data = True

    def translate_data(self, model_state):
        translator = DataTranslator(self.required_plots, model_state)
        return translator.figure_data, translator.plot_data

    def plot_it(self, figure_data, plot_data):
        if self.plotter is None:
            self.plotter = Plotter(figure_data, plot_data, pause_func=self._pause_app, end_app_func=self._end_app)
        else:
            self.plotter.plot(plot_data)
