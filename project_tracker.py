# -*- coding: utf-8 -*-
""" No main, don't run TODO test main? """

import re
from project_files_tracker import FileTracker
from project_metadata import ProjectMetadata


class ProjectID:
    """ Keeps track of project id:
    - fandom_abr
    - raw_title
    - safe_title
    - title_abr

    Used by ProjectTracker """

    def __init__(self, fandom_abr="", raw_title=""):
        self.fandom_abr = fandom_abr if fandom_abr else input("fandom abr: ")
        self.raw_title = raw_title if raw_title else input("full project title: ")
        self.safe_title = self._get_safe_title()
        self.title_abr = self._get_title_abr()

    def _get_safe_title(self):
        """ Returns a version of the title that is safe for paths """
        title = self.raw_title
        title = title.replace(".", ",")  # . would be interpreted as a file extension
        title = title.replace("/", " ")  # / would be interpreted as a subfile or folder
        return title

    def _get_title_abr(self):
        """ Returns the project abbreviation, created from the title initials """
        title = self.raw_title.lower()  # to lowercase
        title = re.sub(r'[^\w^ ]', '', title)  # remove non-alpha characters
        words = title.split(" ")  # split on spaces
        words = [word.strip() for word in words if word]  # remove any additional whitespaces
        initials = [word[0] for word in words]  # get initials
        abr = "".join(initials)  # get string
        return abr


class ProjectTracker:
    """ Keeps track of all project info:
    - id
    - metadata
    - files """

    def __init__(self, fandom_abr:str="", raw_title:str="", mode:str="saved", verbose:bool=True):
        self._verbose = verbose
        self.id = ProjectID(fandom_abr, raw_title)
        self.files = FileTracker(self.id, verbose)
        self.metadata = ProjectMetadata(self, mode, verbose)

    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    ##### what's the use of this class exactly? cf main, template generation, etc
