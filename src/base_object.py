# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" Base verbose object """


class DebugError(Exception):
    def __init__(self, message) -> None:
        super().__init__("DEBUG "+message)


class BaseObject:
    """ Base class for everything """

    def __init__(self, verbose=True):
        self._verbose = verbose

    def _vprint(self, string:str, end:str="\n") -> None:
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)
    
    def __getstate__(self):
        """ Overwritten to exclude private attributes in jsonpickle
        https://stackoverflow.com/questions/18147435/how-to-exclude-specific-fields-on-serialization-with-jsonpickle """
        state = self.__dict__.copy()
        attributes = list(state.keys())
        for att in attributes:
            if att.startswith('_'):
                state.pop(att)
        return state

    def __setstate__(self, state):
        """ Overwritten to exclude private attributes in jsonpickle
        https://stackoverflow.com/questions/18147435/how-to-exclude-specific-fields-on-serialization-with-jsonpickle """
        self.__dict__.update(state)

