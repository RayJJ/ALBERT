import matplotlib
import matplotlib .pyplot as plt
import matplotlib.style
from mpl_toolkits.axes_grid1 import make_axes_locatable

from abs_plotter import AbsPlotter
from constants import *
from model_spec import UPS, DPS
from utils import contrast_to, my_xkcd


class Plotter(AbsPlotter):
    """
    Plotter creates a plot from a user supplied figure specification and a list of subplot specifications.
    All specifications must have been pre-processed by a Translator instance, to embed necessary data.

    The user's figure specification is a dictionary of the form:

    {'type': 'figure', 'title': 'Test Figure Title'},

    The user's list of subplot specifications is a list of dictionaries of the form:

    [
        {'type': 'cell-map', 'sub-plot': (1, 1), 'module': 'md-01'},
        {'type': 'cell-map', 'sub-plot': (1, 1), 'module': 'md-02'},
        {'type': 'heatmap',  'sub-plot': (1, 2), 'module': 'md-01', 'variable': 'potential'},
        {'type': 'heatmap',  'sub-plot': (1, 2), 'module': 'md-02', 'variable': 'potential'},
        {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-02', 'variable': 'potential',
                             'items': 'cells', 'item-keys': ['se-16']},
        {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-01', 'variable': 'potential',
                             'items': 'cells', 'item-keys': ['ne-08', 'ne-09', 'ne-10']},
        {'type': 'lines',    'sub-plot': (2, 2), 'module': 'md-01', 'variable': 'strength',
                             'items': 'synapses',  'item-keys': ['sy-08', 'sy-11', 'sy-14']},
        {'type': 'lines',    'sub-plot': (2, 1), 'module': 'md-01', 'variable': 'potential',
                             'items': 'dendrites',  'item-keys': ['de-08', 'de-11', 'de-14']},
        {'type': 'lines',    'sub-plot': (2, 2), 'module': 'md-01', 'variable': 'potential',
                             'items': 'cells',  'item-keys': ['mo-14']}
    ]

    All keywords are defined as string constants in the constants.py module for use in the Plotter code.

    The module-keys and item-keys are created automatically by the app.
    Cells, Axons, Dendrites, Spines and Synapses are assigned two-digit references in order of their creation.
    These are then prepended with a two-character type identifier, eg:
        md-01 = module 01
        de-01 = dendrite 01
        ax-01 = axon 01
        sy-01 = synapse 01
        sp-01 = spine 01
        ne-01 = neuron 01
        se-02 = sensor 02
        mo-03 = motor 02
    The id numbers are globally unique within multi-module models. Note that the for ne- se- mo-,
    the id numbers are cell-unique, ie a neurons, sensors and motors cannot share the same id number.

    For reference, the keys assigned to all elements of the user's model are printed near the start of the app.log file.

    """

    class SubPlot(AbsPlotter.AbsSubPlot):
        """
        SubPlot encapsulate plot-library specific subplots and dispatches plot_requests to
        relevant plot() functions eg: in HeatMap and CellMap instances.
        """

        class Lines(AbsPlotter.AbsSubPlot.AbsLines):
            """
            Lines holds a collection of lines for a subplot
            """

            class Line(AbsPlotter.AbsSubPlot.AbsLines.AbsLine):
                """
                Line holds a single line for a subplot.

                The line data is initialised to the default (y-base) value over x-range.
                The first real value is appended.
                The line and its x-axis scrolls to the left as new data is added at the right.
                """

                def __init__(self, subplot: any, key: str, value: float, x_range: tuple, y_base: float):
                    """
                    Set the x-range and default y values for a new line in the required subplot.

                    :param subplot: plot-library specific subplot object
                    :param key: unique key for the line (shown in legend)
                    :param value: first non-default y-value for right-hand end of line
                    :param x_range: range of x axis, from left to right
                    :param y_base: default ('resting') value for y
                    """
                    self.subplot = subplot
                    self.key = key
                    start = x_range[0] * DPS
                    end = x_range[1] * DPS
                    # set x, y values to x_range and y_base respectively
                    self.x = [float(x / DPS) for x in range(start, end)]
                    self.y = [y_base for _ in range(start, end)]
                    self.y[-1] = value
                    self.line_object = subplot.plot(self.x, self.y, label=key)[0]  # plot-library specific call

                def plot(self, value: float):
                    """
                    Update the right-hand end of this line with a new y-value

                    :param value: new y-value
                    :return: None
                    """
                    self.x.append(self.x[-1] + 1)
                    self.y.append(value)
                    self.line_object.set_xdata(self.x)
                    self.line_object.set_ydata(self.y)

            def __init__(self, subplot: any, plot_request: dict):
                """
                Create the requested Line instances in the requested subplot.

                :param subplot: plot-library specific subplot object.
                :param plot_request: dictionary specifying one-or-more lines to be instantiated.
                """
                self.line_dict = {}
                self.subplot = subplot
                for key, value in plot_request[Y_DATA].items():
                    self.line_dict[key] = self.Line(subplot, key, value,
                                                    plot_request[X_RANGE], plot_request[Y_BASE])
                self._legend(subplot, plot_request[VARIABLE])

            def plot(self, plot_request: dict):
                """
                Update each of the lines in the supplied lines request.

                :param plot_request: dictionary specifying one-or-more lines to be updated with the included values.
                :return: None
                """
                x_lim = self.subplot.get_xlim()
                for key, value in plot_request[Y_DATA].items():
                    self.line_dict[key].plot(value)
                self.subplot.set_xlim(tuple(map(lambda x: x + 1 / DPS, x_lim)))

            def _legend(self, subplot, title: str = None):
                """
                Show a legend in the upper-left of this multi-line subplot.

                :param subplot: plot-library specific subplot object.
                :param title: Title for the legend (defaults to None).
                :return:
                """
                subplot.legend(loc='upper left', title=title)

        class CellMap(AbsPlotter.AbsSubPlot.AbsCellMap):
            """
            CellMap creates a 2D map of the cells, axons and dendrites of a single module.

            Active elements of the model are highlighted by setting alpha = 1.0
            """

            def __init__(self, subplot: any, plot_request: dict):
                """
                Create the requested cell map in the requested subplot.

                The graphical representations of each component and their active states are stored in dictionaries.

                :param subplot: plot-library specific subplot object.
                :param plot_request: dictionary specifying details of the cells, dendrites and axons to be plotted.
                """
                self.patch_dict = {}
                # active state (True = active) of cells and cell components
                self.active_dict = {}
                self.subplot = subplot
                for key, cell in plot_request[CELLS].items():
                    self.patch_dict[key] = self._plot_cell(cell, subplot)
                    self.active_dict[key] = cell[ACTIVE]
                for key, dendrite in plot_request[DENDRITES].items():
                    self.patch_dict[key] = self._plot_item(dendrite, subplot, DENDRITES)
                    self.active_dict[key] = dendrite[ACTIVE]
                for key, axon in plot_request[AXONS].items():
                    self.patch_dict[key] = self._plot_item(axon, subplot, AXONS)
                    self.active_dict[key] = axon[ACTIVE]
                self._cell_map_legend(subplot)

            def plot(self, plot_request: dict):
                """
                Update this cellmap with the data in the supplied plot_request

                :param plot_request: dictionary containing new data for the cellmap
                :return: None
                """
                alphas = {True: 1.0, False: 0.5}
                for key, cell in plot_request[CELLS].items():
                    if self.active_dict[key] != cell[ACTIVE]:
                        self.active_dict[key] = cell[ACTIVE]
                        self.patch_dict[key].set_alpha(alphas[cell[ACTIVE]])
                for key, dendrite in plot_request[DENDRITES].items():
                    if self.active_dict[key] != dendrite[ACTIVE]:
                        self.active_dict[key] = dendrite[ACTIVE]
                        self.patch_dict[key].set_alpha(alphas[dendrite[ACTIVE]])
                for key, axon in plot_request[AXONS].items():
                    if self.active_dict[key] != axon[ACTIVE]:
                        self.active_dict[key] = axon[ACTIVE]
                        self.patch_dict[key].set_alpha(alphas[axon[ACTIVE]])

            def _plot_item(self, item_spec: dict, subplot: any, item_type: str):
                """
                Plot an item (axon or a dendrite) as a colored polyline within a cell map.

                :param item_spec: dictionary specifying the details of the item.
                :param subplot: plot-library specific subplot object
                :param item_type: type keyword, either 'axon' or 'dendrite'
                :return: graphic patch representing this item.
                """
                # swap coords: (row, col) -> (x, y)
                locations = [(location[1], location[0]) for location in item_spec[LOCATIONS]]
                with my_xkcd(scale=5, length=60, randomness=5):
                    patch = plt.Polygon(locations, label=item_spec[KEY], closed=None, linewidth=3, fill=None,
                                        edgecolor=CELL_MAP_COLOR[item_type], alpha=0.4, zorder=0.4)
                subplot.add_patch(patch)
                return patch

            def _plot_cell(self, cell_spec: dict, subplot: any):
                """
                Plot a cell (neuron, sensor or motor) as a colored disc within a cell map.

                :param cell_spec: dictionary specifying the details of the cell.
                :param subplot: plot-library specific subplot object
                :return: graphic patch representing this cell.
                """
                # swap coords: (row, col) -> (x, y)
                cell_type = cell_spec[CELL_TYPE]
                location = (cell_spec[LOCATION][1], cell_spec[LOCATION][0])
                with my_xkcd(scale=5, length=30, randomness=5):
                    patch = plt.Circle(location, label=cell_spec[KEY], zorder=0.5, radius=SOMA_RADIUS,
                                       fc=CELL_MAP_COLOR[cell_type], alpha=0.5)
                subplot.add_patch(patch)
                subplot.text(location[0], location[1], str(cell_spec[KEY])[-2:], va='center', ha='center',
                             color=contrast_to(CELL_MAP_COLOR[cell_type]))
                return patch

            def _cell_map_legend(self, subplot: any, title: str = None):
                """
                Show a cell-map legend at upper left of this cell-map subplot.

                :param subplot: plot-library specific subplot object.
                :param title: Title for the legend (defaults to None).
                :return: None
                """
                with my_xkcd(scale=5, length=20, randomness=2):
                    legend_elements = [plt.Line2D([0], [0], color=CELL_MAP_COLOR['axon'],
                                                  lw=2, label='Axons'),
                                       plt.Line2D([0], [0], color=CELL_MAP_COLOR['dendrite'],
                                                  lw=3, label='Dendrites'),
                                       plt.Line2D([0], [0], marker='o', color='black',
                                                  markerfacecolor=CELL_MAP_COLOR['motor'],
                                                  markersize=12, label='Motors', alpha=0.7),
                                       plt.Line2D([0], [0], marker='o', color='black',
                                                  markerfacecolor=CELL_MAP_COLOR['neuron'],
                                                  markersize=12, label='Neurons', alpha=0.7),
                                       plt.Line2D([0], [0], marker='o', color='black',
                                                  markerfacecolor=CELL_MAP_COLOR['sensor'],
                                                  markersize=12, label='Sensors', alpha=0.7)]
                subplot.legend(handles=legend_elements, title=title, loc='upper left')

        class HeatMap(AbsPlotter.AbsSubPlot.AbsHeatMap):
            """
            Create a heatmap of cell voltages for the requested module in the requested subplot.

            :param subplot: plot-library specific subplot object.
            :param plot_request: dictionary specifying details of the cells, dendrites and axons to be plotted.
            """

            def __init__(self, subplot: any, plot_request: dict):
                """
                Create the requested heatmap in the requested subplot.

                :param subplot: plot-library specific subplot object.
                :param plot_request: dictionary specifying a grid of voltages for the module to be plotted.
                """
                if plot_request[PLOT_TYPE] != HEATMAP:
                    raise Exception(f'HeatMap requested with type "{plot_request[PLOT_TYPE]}"')
                self.image = None
                # if current_subplot has no image
                divider = make_axes_locatable(subplot)
                cax = divider.append_axes('right', '5%', pad='3%')
                self.image = subplot.imshow(
                    plot_request[XY_DATA],
                    vmin=plot_request[V_MIN],
                    vmax=plot_request[V_MAX],
                    interpolation='gaussian')
                self.image.set_cmap('jet')
                plt.colorbar(self.image, cax=cax)

            def plot(self, plot_request: dict):
                """
                Update this heatmap with the data in the supplied plot_request

                :param plot_request: dictionary containing new data for the heatmap
                :return: None
                """
                self.image.set_data(plot_request[XY_DATA])

        def __init__(self, subplot):
            """
            Initialise this subplot.

            :param subplot: plot-library specific subplot object.
            """
            self.subplot = subplot
            self.plot_object = None

        def plot(self, plot_request):
            """
            Dispatch a plot_request to the relevant specialised class.
            Specialised plot objects are created when first requested and then updated through
            calls to the object's plot() function.

            :param plot_request: dictionary containing new data for the subplot
            :return: None
            """
            plot_type = plot_request[PLOT_TYPE]
            if plot_type == LINES:
                if self.plot_object is None:
                    self.plot_object = self.Lines(self.subplot, plot_request)
                else:
                    self.plot_object.plot(plot_request)
            elif plot_type == CELL_MAP:
                if self.plot_object is None:
                    self.plot_object = self.CellMap(self.subplot, plot_request)
                else:
                    self.plot_object.plot(plot_request)
            elif plot_type == HEATMAP:
                if self.plot_object is None:
                    self.plot_object = self.HeatMap(self.subplot, plot_request)
                else:
                    self.plot_object.plot(plot_request)
            else:
                raise (Exception, f'Unrecognised Plot Type "{plot_type}" in plot request.')

    def __init__(self, figure_spec: dict, plot_requests: list, end_app_func: callable = None):
        """
        Create Plotter() object to provide a data-drive plotting interface for the modelling app.

        :param figure_spec: dictionary of figure specification items (see Plotter() class doc.
        :param plot_requests:
        :param end_app_func:
        """
        self.subplots = None  # dict with key: subplot tuple; value: subplot object
        self.canvas = None
        self._set_plot_config()
        self.canvas, self.subplots = self._make_plot(end_app_func, figure_spec)
        self._set_subplot_configs(plot_requests)
        self.data_batch = 0
        plt.ion()

    def _set_plot_config(self):
        """
        Do plot-library specific set-up.

        :return: None
        """
        # === start plot-library specific code
        matplotlib.use('gtk3agg')
        # save ca. 25% cpu time
        matplotlib.style.use('fast')
        # theme the window and its widgets
        plt.style.use('dark_background')
        # === end plot-library specific code

    def _make_plot(self, end_app_func: callable, figure_spec: dict):
        """
        Make a plot-library specific window that ends the app when closed.
        Plot-library specific subplots and figure layout are handled here.
        Delegates app subplot creation to _make_subplots() function.

        :param end_app_func: function that shuts down the app and its threads
        :param figure_spec: app figure-spec dictionary (see Plotter() class doc)
        :return: plot-library specific canvas object
                 plot-library specific array of sub-plots (eg Matplotlib Axes)
        """
        # === start plot-library specific code
        # create figure and axes
        plot, axes = plt.subplots(figure_spec[DIMENSIONS][0], figure_spec[DIMENSIONS][1],
                                  squeeze=False)  # squeeze=False forces 2D axes array
        plot.suptitle(figure_spec[TITLE], fontsize=16)
        plt.subplots_adjust(wspace=0.35, hspace=0.35)
        canvas = plot.canvas
        canvas.mpl_connect('close_event', end_app_func)
        # === end plot-library specific code
        subplots = self._make_subplots(axes, figure_spec)
        return canvas, subplots

    def _make_subplots(self, axes: any, figure_data: dict):
        """
        Make a dictionary of app Subplot() objects that wrap plot-library specific subplots.

        :param axes: plot-library specific subplot objects.
        :param figure_data: dictionary of figure specification.
        :return: app-specific subplot objects.
        """

        subplots = {}
        # store required axes in subplots dictionary and hide others.
        for row in range(1, figure_data[DIMENSIONS][0]+1):
            for col in range(1, figure_data[DIMENSIONS][1]+1):
                if (row, col) in figure_data[SUBPLOTS]:
                    subplots[(row, col)] = self.SubPlot(axes[row-1, col-1])  # plot-library specific code
                else:
                    axes[row-1, col-1].set_visible(False)  # plot-library specific code
        return subplots

    def _set_subplot_configs(self, plot_requests: list):
        """
        Set configuration of each subplot.
            Typically, configuration items are fixed for the duration of the plotting
            such as: subplot titles and subplot axis labels.

        :param plot_requests: list of plot request dictionaries (see Plotter() class doc).
        :return: None
        """
        for request in plot_requests:
            # === start plot-library specific code
            self.subplots[request[SUBPLOT]].subplot.set_title(request[TITLE])
            self.subplots[request[SUBPLOT]].subplot.set_xlim(request[X_RANGE][0], request[X_RANGE][1])
            self.subplots[request[SUBPLOT]].subplot.set_ylim(request[Y_RANGE][0], request[Y_RANGE][1])
            self.subplots[request[SUBPLOT]].subplot.set_xlabel(request[X_LABEL])
            self.subplots[request[SUBPLOT]].subplot.set_ylabel(request[Y_LABEL])
            self.subplots[request[SUBPLOT]].subplot.set_autoscalex_on(False)
            self.subplots[request[SUBPLOT]].subplot.set_autoscaley_on(False)
            # === plot-library specific code

    def _draw(self):
        """
        Draw all pending graphics.

        :return: None
        """
        # === start plot-library specific code
        self.canvas.flush_events()
        plt.pause(0.01)
        # === end plot-library specific code

    def plot(self, plot_requests: list):
        """
        Dispatch each plot request to the plot function of its requested subplot.

        :param plot_requests: list of plot request dictionaries (see Plotter() class doc).
        :return: None
        """
        for request in plot_requests:
            self.subplots[request[SUBPLOT]].plot(request)
        self.data_batch += 1
        if self.data_batch % DPS == 0:
            self._draw()
