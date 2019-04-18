"""
    Program: ALBERT
    Module: utils.py

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
import numpy as np
import math
import time
import matplotlib


from constants import NS_PER_MS


def timed_call(function, **kwargs):
    t_start = math.ceil(time.perf_counter_ns())
    function(**kwargs)
    return math.ceil(time.perf_counter_ns()) - t_start


def log_time(function, message, **kwargs):
    call_time = timed_call(function, **kwargs)
    logging.info(f"{message} =\t{call_time / NS_PER_MS: 7.2f} ms")


def loc_to_point(dimensions: tuple, location: tuple) -> tuple:
    # location is (row, col) rows range 0..dimension[0]-1 from base to top
    # point is (x, y) x = col, y = num_rows - row - 1
    return location[1], dimensions[0] - location[0] - 1


def y_bell(x: float, mean: float, sd: float) -> float:
    """
    return y in the range (0.0 ... 1.0) for an x co-ordinate on a bell curve with given mean and sd
    """
    return 2.5 * (1 / (sd * np.sqrt(2 * np.pi)) * np.exp(- (10 * x - mean) ** 2 / (2 * sd ** 2)))


def y_sigmoid(x1: float) -> float:
    # returns y of sigmoid where y = 0..1 for x = -1..1
    return 1.0 / (1.0 + math.exp(-x1 * 10.0))


def contrast_to(background_color: str) -> str:
    """ return text color that contrasts with given background color """
    from colour import Color
    # convert to color object
    background_color = Color(background_color)
    # perceptive luminance - the human eye favors green color
    luminance = (0.299 * background_color.red + 0.587 * background_color.green + 0.114 * background_color.blue)
    # choose best contrasting text color (0.41 found to be better for chosen palette than default 0.5)
    return 'black' if luminance > 0.5 else 'white'


def my_xkcd(scale=1, length=100, randomness=2):
    """
    Turn on `xkcd <https://xkcd.com/>`_ sketch-style drawing mode.
    This will only have effect on things drawn after this function is
    called.

    For best results, the "Humor Sans" font should be installed: it is
    not included with matplotlib.

    Parameters
    ----------
    scale : float, optional
        The amplitude of the wiggle perpendicular to the source line.
    length : float, optional
        The length of the wiggle along the line.
    randomness : float, optional
        The scale factor by which the length is shrunken or expanded.

    Notes
    -----
    This function works by a number of rcParams, so it will probably
    override others you have set before.

    If you want the effects of this function to be temporary, it can
    be used as a context manager, for example::

        with plt.xkcd():
            # This figure will be in XKCD-style
            fig1 = plt.figure()
            # ...

        # This figure will be in regular style
        fig2 = plt.figure()
    """
    if matplotlib.rcParams['text.usetex']:
        raise RuntimeError(
            "xkcd mode is not compatible with text.usetex = True")

    from matplotlib import patheffects
    return matplotlib.rc_context({
        'font.family': ['xkcd', 'Humor Sans', 'Comic Sans MS'],
        'font.size': 12.0,
        'path.sketch': (scale, length, randomness),
        'path.effects': [patheffects.withStroke(linewidth=2, foreground="b")],
        'axes.linewidth': 1.5,
        'lines.linewidth': 2.0,
        'figure.facecolor': 'white',
        'grid.linewidth': 0.0,
        'axes.grid': False,
        'axes.unicode_minus': False,
        'axes.edgecolor': 'black',
        'xtick.major.size': 8,
        'xtick.major.width': 3,
        'ytick.major.size': 8,
        'ytick.major.width': 3,
    })
