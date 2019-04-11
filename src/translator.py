import logging
from copy import deepcopy

import numpy as np

from constants import *
from model_spec import REST_POTENTIAL, MAX_STRENGTH


class DataTranslator:

    def __init__(self, plot_request, model_data):
        self.figure_data, self.plot_request = self.split_request(deepcopy(plot_request))
        self.model_data = model_data
        self.sub_plots = []
        self.modules = set([])
        self.plot_data = []
        self.translate()

    @staticmethod
    def split_request(plot_request):
        fig_request = None
        plt_request = []
        for request in plot_request:
            if request[PLOT_TYPE] == FIGURE:
                fig_request = request
            else:
                plt_request.append(request)
        return fig_request, plt_request

    def translate(self):
        self.translate_figure()
        for item in self.plot_request:
            if item[PLOT_TYPE] == CELL_MAP:
                self.translate_cell_map(item)
            elif item[PLOT_TYPE] == HEATMAP:
                self.translate_heat_map(item)
            elif item[PLOT_TYPE] == LINES:
                self.translate_lines(item)
            else:
                logging.info(f"Unrecognised plot type: {item['type']}")

    def translate_figure(self):
        def item_key(item: dict):
            return item[MODULE]
        self.plot_request.sort(key=item_key)
        max_rows = 0
        max_cols = 0
        module_count = 0
        for item in self.plot_request:
            module_num = int(item[MODULE][-2:])
            module_count = max(module_count, module_num)
            max_rows = max(max_rows, item[SUBPLOT][0])
            max_cols = max(max_cols, item[SUBPLOT][1])
            # this requires plot_requests to be sorted in order of module keys
            item[SUBPLOT] = (item[SUBPLOT][0], item[SUBPLOT][1] + max_cols * (module_num - 1))
            self.sub_plots.append(item[SUBPLOT])
        self.figure_data[DIMENSIONS] = (max_rows, max_cols * module_count)
        self.figure_data[SUBPLOTS] = self.sub_plots
        self.figure_data[TIME_ALIVE_CYCLES] = self.model_data[TIME_ALIVE_CYCLES]

    def translate_cell_map(self, request):
        module_data = self.model_data[MODULES][request[MODULE]]
        dimensions = module_data[DIMENSIONS]
        request[X_LABEL] = 'Columns'
        request[Y_LABEL] = 'Rows'
        request[X_RANGE] = (- 0.5, dimensions[1] - 0.5)
        request[Y_RANGE] = (- 0.5, dimensions[0] - 0.5)
        request[TITLE] = module_data[DESCRIPTION] + f' {request[MODULE]}'
        request[CELLS] = module_data[CELLS]
        request[AXONS] = module_data[AXONS]
        request[DENDRITES] = module_data[DENDRITES]
        request[SPINES] = module_data[SPINES]
        request[SYNAPSES] = module_data[SYNAPSES]
        self.plot_data.append(request)

    def translate_heat_map(self, request):
        # adds: data['xy-data'], data['v-min'], data['v-max']
        module_data = self.model_data[MODULES][request[MODULE]]
        dimensions = module_data[DIMENSIONS]
        request[V_MIN] = -100
        request[V_MAX] = 20
        request[X_LABEL] = 'Columns'
        request[Y_LABEL] = 'Rows'
        request[X_RANGE] = (- 0.5, dimensions[1] - 0.5)
        request[Y_RANGE] = (- 0.5, dimensions[0] - 0.5)
        request[TITLE] = module_data[DESCRIPTION] + f' {request[MODULE]}'
        variable = request[VARIABLE]
        xy_data = np.full(dimensions, REST_POTENTIAL)
        for key, node in module_data[NODES].items():
            row = key[0]
            column = key[1]
            xy_data[row][column] = node[variable]
        request[XY_DATA] = xy_data
        self.plot_data.append(request)

    def translate_lines(self, request):
        variable = request[VARIABLE]
        items = request[ITEMS]
        if variable == POTENTIAL:
            request.update(
                {TITLE: f'Potentials (mV) for {items}\n in module {request[MODULE]}',
                    Y_LABEL: 'Potentials (mV)',  X_LABEL: 'Time (sec)',
                    Y_RANGE: [-150.0, 150.0],    X_RANGE: [-50, 0],     Y_BASE: REST_POTENTIAL})
        elif variable == LENGTH:
            request.update(
                {TITLE: f'Length (microns) for {items}\n in module {request[MODULE]}',
                    Y_LABEL: 'Length (microns)', X_LABEL: 'Time (sec)',
                    Y_RANGE: [0.0, 1.5],         X_RANGE: [-50, 0],     Y_BASE: REST_POTENTIAL})
        elif variable == STRENGTH:
            request.update(
                {TITLE: f'Strength (ion channels) for {items}\n in module {request[MODULE]}',
                    Y_LABEL: 'Strength (ion channels)',  X_LABEL: 'Time (sec)',
                    Y_RANGE: [0.0, MAX_STRENGTH * 1.1],  X_RANGE: [-50, 0],     Y_BASE: 0})
        else:
            request.update(
                {TITLE: f'Unrecognised variable "{variable}"" requested',
                    Y_LABEL: 'None', X_LABEL: 'None',
                    Y_RANGE: [0, 1], X_RANGE: [-50, 0], Y_BASE: 0})
        # copy data values to the expanded request
        data = self.model_data[MODULES][request[MODULE]]
        item_keys = request[ITEM_KEYS]
        y_data = {}
        for key in item_keys:
            y_data[key] = data[items][key][variable]

        request[Y_DATA] = y_data
        self.plot_data.append(request)
