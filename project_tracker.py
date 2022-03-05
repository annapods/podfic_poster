# -*- coding: utf-8 -*-
""" No main, don't run TODO test main? """

import os, re
import sys
from dataclasses import dataclass, field
from collections import namedtuple
from typing import List, Any


# Dataclass structures to organise files
# couldn't make it work with default factories (somehow the init method never included the first
# attribute) so redifining init each time...
# default factories https://stackoverflow.com/questions/69564830/python-dataclass-setting-default-list-with-values
# empty_list = field(default_factory=lambda: [])
# empty_str = field(default_factory=lambda: "")

@dataclass
class CompressedFileTracker:
    compressed: List[str]
    raw: List[str]
    def __init__(self, compressed=[], raw=[]):
        self.compressed = compressed
        self.raw = raw

@dataclass
class FormattedFileTracker:
    formatted: List[str]
    unformatted: List[str]
    def __init__(self, formatted=[], unformatted=[]):
        self.formatted = formatted
        self.unformatted = unformatted

@dataclass
class TemplateFileTracker:
    ao3: str
    dw: str
    def __init__(self, ao3="", dw=""):
        self.ao3 = ao3
        self.dw = dw

@dataclass
class FileTracker:
    info: str
    template: TemplateFileTracker
    audio: CompressedFileTracker
    cover: CompressedFileTracker
    def __init__(self, info="",
        template=TemplateFileTracker(),
        audio=CompressedFileTracker(FormattedFileTracker(), FormattedFileTracker()),
        cover=CompressedFileTracker()):
        self.info = info
        self.template = template
        self.audio = audio
        self.cover = cover


class ProjectTracker:
    """ Keeping track of project title, folder, files, etc
    - title
        - raw
        - safe_for_path
        - abr
    files
        - info
        - template
            - ao3
            - dw
            TODO add tracker?
        - cover
            - compressed
            - raw
        - audio
            - compressed
                - formatted
                - unformatted
            - raw
                - formatted
                - unformatted """

    wips_folder = "../../../Musique/2.5 to post"
    tracker = ""

    def __init__(self, fandom="", title="", folder="", verbose=True):
        """ Any info left empty will be infered or asked in the command line interface """
        self._verbose = verbose

        self.fandom = fandom if fandom else input("fandom abr: ")
        
        raw_title = title if title else input("project title: ")
        safe_title = self.get_safe_title(raw_title)
        title_abr = self.get_title_abr(raw_title)
        TitleTracker = namedtuple('TitleTracker', ['raw', 'safe_for_path', 'abr'])
        self.title = TitleTracker(raw=raw_title, safe_for_path=safe_title, abr=title_abr)

        self.folder = folder if folder else self._get_folder()
        self._check_folder()

        self.files = FileTracker()
        self.update_file_paths()


    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    def _check_folder(self):
        """ Checks which folder to use, creating it if necessary
        -> yes
            -> use exising folder or input name?
        -> no
            -> create or quit? """

        # Check that the folder exists
        if os.path.exists(self.folder):

        # If yes, ask for confirmation
            choice = input(f"use existing folder {self.folder}?" \
                + " nothing for yes, quit for quit, new name otherwise")
            if choice == "quit":
                print("quitting!")  # TODO
                sys.exit()
            elif choice != "":
                self.folder = choice
                self._check_folder()
            else:
                return

        # If the folder doesn't exist, offer to create it
        else:
            print(f"/!\\ that folder doesn't exist yet: {self.folder}")
            choice = input("create it? nothing for yes, quit for quit")
            if not choice:
                os.mkdir(self.folder)

        # Or quit, if you want to go back and input another fandom and title
            elif choice == "quit":
                sys.exit()


    def get_safe_title(self, title):
        """ Returns a version of the title that is safe for paths """
        title = title.replace(".", ",")
        title = title.replace("/", " ")
        return title


    def get_title_abr(self, title):
        """ Returns the project abbreviation, created from the title initials """
        title = title.lower()
        title = re.sub(r'[^\w^ ]', '', title)
        words = title.split(" ")
        initials = [word[0] for word in words]
        abr = "".join(initials)
        return abr


    def _get_folder(self):
        """ Returns the path to the project folder, ex: "wips_folder/fandom - project" """
        return os.path.join(ProjectTracker.wips_folder, f"{self.fandom} - {self.title.abr}")


    def update_file_paths(self):
        """ Saves the paths to the various project files to the tracker """
        self.files.info = os.path.join(self.folder, f'{self.title.abr} info.yaml')
        self.files.template.dw = os.path.join(self.folder, f'{self.title.abr} dw.txt')
        self.files.template.ao3 = os.path.join(self.folder, f'{self.title.abr} ao3.csv')
        self.files.audio.compressed.unformatted = self.get_files(self.title.abr, ".mp3")
        self.files.audio.raw.unformatted = self.get_files(self.title.abr, ".wav")
        self.files.audio.compressed.formatted = self.get_files(self.title.safe_for_path, ".mp3")
        self.files.audio.raw.formatted = self.get_files(self.title.safe_for_path, ".wav")
        self.files.cover.compressed = self.get_files(self.title.abr, ".png")
        self.files.cover.raw = self.get_files(self.title.abr, ".svg")
        self.files.fic = self.get_files(".html")


    def get_files(self, contains="", endswith=""):
        """ Looks for files in the given folder which name contains and ends with the
        given strings """
        files = [
            os.path.join(self.folder, file)
            for file in os.listdir(self.folder)
            if re.match(f".*{contains}.*{endswith}$", file)
        ]
        return files
