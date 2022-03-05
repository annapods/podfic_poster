# -*- coding: utf-8 -*-


class Ao3Poster:
    """ Ao3 posting helper! """

    def __init__(self, file_info, work_info, verbose=True):
        self._verbose = verbose
        self.files = file_info
        self.work = work_info

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def post_podfic(self):
        """ TODO """
        self._vprint("Drafting podfic post to ao3...", end=" ")
        pass
        self._vprint("done!")
