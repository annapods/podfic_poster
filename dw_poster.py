# -*- coding: utf-8 -*-
"""
TODO
"""


class DWPoster:
    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = project_info
        self._work = work_info

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def post_podfic(self):
        self._vprint("Drafting podfic post to dw...", end=" ")
        pass
        self._vprint("done!")
        