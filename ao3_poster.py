# -*- coding: utf-8 -*-
"""
TODO
"""


class Ao3Poster:
    def __init__(self, file_info, work_info, verbose=True):
        self.verbose = verbose
        self.files = file_info
        self.work = work_info

    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)

    def post_podfic(self):
        self.vprint("Drafting podfic post to ao3...", end=" ")
        pass
        self.vprint("done!")
