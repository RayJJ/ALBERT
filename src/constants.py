# code names

GTK = 'gtk'
MATPLOT = 'matplot'
TIME_ALIVE_CYCLES = 'time_alive'

DIE = 'die'

HEATMAP = 'heatmap'
CELL_MAP = 'cell-map'
LINES = 'lines'

PLOT_TYPE = 'type'
SUBPLOT = 'sub-plot'
SUBPLOTS = 'sub-plots'
FIGURE = 'figure'
DESCRIPTION = 'description'
TITLE = 'title'
X_LABEL = 'x-label'
Y_LABEL = 'y-label'
X_RANGE = 'x-range'
Y_RANGE = 'y-range'
Y_DATA = 'y-data'
X_DATA = 'x-data'
XY_DATA = 'xy-data'
Y_BASE = 'y-base'
LOCATION = 'location'
LOCATIONS = 'locations'
VARIABLE = 'variable'
ITEMS = 'items'
ITEM_KEYS = 'item-keys'
V_MIN = 'v-min'
V_MAX = 'v-max'

KEY = 'key'
CELLS = 'cells'
CHILDREN = 'children'
SOMA = 'soma'
CELL_TYPE = 'type'
NEURON = 'neuron'
NEURONS = 'neurons'
MOTOR = 'motor'
MOTORS = 'motors'
SENSOR = 'sensor'
SENSORS = 'sensors'
AXON = 'axon'
AXONS = 'axons'
DENDRITE = 'dendrite'
DENDRITES = 'dendrites'
SYNAPSE = 'synapse'
SYNAPSES = 'synapses'
SPINE = 'spine'
SPINES = 'spines'
MODULE = 'module'
MODULES = 'modules'
DIMENSIONS = 'dimensions'
NODES = 'nodes'
BRIDGE = 'bridge'
BRIDGES = 'bridges'
FROM_LOCATION = 'from_location'
TO_LOCATION = 'to_location'
FROM_MODULE_ID = 'from_module_id'
TO_MODULE_ID = 'to_module_id'

LENGTH = 'length'
SPINE_LENGTH = 'length'
STRENGTH = 'strength'
GROWTH_RATE = 'growth-rate'
SHRINK_RATE = 'shrink-rate'
CONNECTED = 'connected'
DECAY_RATE = 'decay-rate'
BIAS = 'bias'
ACTIVE = 'active'
EXCITER = 'exciter'
FIRING_THRESHOLD = 'firing_threshold'
POTENTIAL = 'potential'
INJECTED_POTENTIAL = 'injected_potential'


# presentation values

WIN_X, WIN_Y = 1.0, 0.5             # window as proportions of full screen
CANVAS_X, CANVAS_Y = 1200, 1024     # window scrolls if canvas is bigger
SCROLL_WINDOW_BORDER = 10
SUBPLOT_ROWS = 1

MATPLOT_THEME = 'dark_background'
PLOT_TYPES = ['heatmap', 'line', 'cell_map']
# ToDo: remove ambiguous/duplicate names in plot code
CELL_MAP_COLOR = {'neuron': 'cyan', 'sensor': 'magenta', 'motor': 'green', 'dendrite': 'blue', 'axon': 'orange',
                  'neurons': 'cyan', 'sensors': 'magenta', 'motors': 'green', 'dendrites': 'blue', 'axons': 'orange'}
SOMA_RADIUS = 0.30


# constant scalars

NS = 1000000000.0  # nanoseconds per second
NS_PER_MS = 1000000.0  # nanoseconds per millisecond
