import abc
from abc import abstractmethod


class AbsUpdatable(metaclass=abc.ABCMeta):

    @abstractmethod
    def on_tick(self):
        """
        interface for all time dependent functions of brain components
        """
        ...

    @abstractmethod
    def on_state_dump(self):
        """
        interface for all state recording functions of brain components
        """
        ...
