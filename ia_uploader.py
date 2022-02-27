# -*- coding: utf-8 -*-
"""
Setup:
ia --config-file './.ia-custom-config' configure
ia configure
TODO
"""

from internetarchive import upload


class IAUploader:
    """ Internet Archive uploading helper! """

    def __init__(self, file_info, work_info, verbose=True):
        self.verbose = verbose
        self.files = file_info
        self.work = work_info


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def upload_audio(self):
        """ Uploads audio files (mp3 and wav) to the ia item """
        self.vprint("Uploading podfic files to ia...", end=" ")
        # self.work.update_info("IA Link", "URL")
        # self.work.update_info("IA Cover Link", "URL")
        # self.work.update_info("IA Streaming Links", "URL")
        pass
        self.vprint("done!")

    def upload_cover(self):
        self.vprint("Uploading cover art to ia...", end=" ")
        pass
        self.vprint("done!")

    def upload_info(self):
        self.vprint("Uploading podfic info to ia...", end=" ")
        pass
        self.vprint("done!")

    def add_description(self):
        self.vprint("Adding podfic link to ia...", end=" ")
        pass
        self.vprint("done!")
