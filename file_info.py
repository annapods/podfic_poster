# -*- coding: utf-8 -*-
"""
Keeping track of files in the folder
"""

import os, re


class FileInfo:
    """
    Keeps track of the project files
    """
    wips_folder = "../../../Musique/2.5 to post"

    def __init__(self, fandom="", project="", verbose=True):
        """
        Fandom and project can be left empty, in which case they will be asked for in the
        command prompt interface.
        """
        self.verbose = verbose
        self.fandom = fandom if fandom else input("fandom abr: ")
        self.project = project if project else input("project abr: ")

        self.folder = os.path.join(FileInfo.wips_folder, f"{self.fandom} - {self.project}")
        if not os.path.exists(self.folder):
            print("/!\ that folder doesn't exist yet")
            if not input("create it? nothing for yes"):
                os.mkdir(self.folder)
            else: self = FileInfo(verbose=verbose)
        
        self.update_file_paths()

    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)### File paths

    def update_file_paths(self):
        self.mp3_wip = self.get_wip_files(".mp3")
        self.wav_wip = self.get_wip_files(".wav")
        self.mp3_final = self.get_final_files("mp3")
        self.wav_final = self.get_final_files("wav")
        self.png = self.get_wip_files(".png")
        self.svg = self.get_wip_files(".svg")
        self.html_fic = self.get_final_files("html")
        self.dw = os.path.join(self.folder, f'{self.project} dw.txt')
        self.ao3 = os.path.join(self.folder, f'{self.project} ao3.csv')
        self.yaml_info = os.path.join(self.folder, f'{self.project} info.yaml')

    def get_final_files(self, contains="mp3"):
        files = [
            os.path.join(self.folder, file)
            for file in os.listdir(self.folder)
            if re.match(f".*{contains}.*", file)
        ]
        return files

    def get_wip_files(self, end):
        """
        Gets you the paths to the files that start with the project abr and end with the end
        Does need project abr in file name
        """
        files = [
            os.path.join(self.folder, file)
            for file in os.listdir(self.folder)
            if re.match(f"{self.project}.*{end}", file)
        ]
        return files
