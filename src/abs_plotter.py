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

