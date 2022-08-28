# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" Base verbose object """


class VerboseObject:
    """ Base class for everything """

    def __init__(self, verbose=True):
        self._verbose = verbose

    def _vprint(self, string:str, end:str="\n") -> None:
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)
