"""
    Program: ALBERT
    Module: abs_plotter.py

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

from abc import abstractmethod


# structure of the app's Plotter:
#
#     class Plotter:
#         class SubPlot:
#             class Lines:
#                 class Line:
#             class CellMap:
#             class HeatMap:

class AbsPlotter:

    class AbsSubPlot:

        class AbsLines:

            class AbsLine:

                @abstractmethod
                def plot(self, value: float):
                    ...

            @abstractmethod
            def plot(self, value: float):
                ...

        @abstractmethod
        def plot(self, value: float):
            ...

        class AbsCellMap:

            @abstractmethod
            def plot(self, value: float):
                ...

        class AbsHeatMap:

            @abstractmethod
            def plot(self, value: float):
                ...

    @abstractmethod
    def plot(self, value: float):
        ...

