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
        self.title = self._get_title(title)
        self.folder = self._get_folder(folder)

        self.files = FileTracker()
        self.update_file_paths()


    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    def _get_folder(self, folder=""):
        """ Returns the path to the project folder, ex: "wips_folder/fandom - project"
        Gets user input on whether to create or reuse a folder
        WARNING gotta do the title and fandom stuff first """

        folder = folder if folder \
            else os.path.join(ProjectTracker.wips_folder, f"{self.fandom} - {self.title.abr}")

        if os.path.exists(folder):
            print(f"found a project folder! {folder}")
            print("you can:")
            print("- use it (hit return without typing anything)")
            print("- quit (type quit and then hit return)")
            print("- use another folder (type the path to the folder then hit return)")
            choice = input()
            if choice == "":
                return folder
            if choice == "quit":
                print("bye!")
                sys.exit()
                return None
            self._get_folder(choice)

        else:
            print(f"/!\\ that folder doesn't exist yet: {folder}")
            print("you can:")
            print("- create it (hit return)")
            print("- quit (type quit)")
            print("- use another folder path (type it into the terminal")
            choice = input()
            if choice == "":
                os.mkdir(folder)
                return folder
            if choice == "quit":
                print("bye!")
                sys.exit()
                return None
            return self._get_folder(choice)


    def _get_title(self, raw_title=""):
        """ Generates safe_for_path and abr titles, returning a named tuple with all versions """

        def get_safe_title(title):
            """ Returns a version of the title that is safe for paths """
            title = title.replace(".", ",")
            title = title.replace("/", " ")
            return title

        def get_title_abr(title):
            """ Returns the project abbreviation, created from the title initials """
            title = title.lower()
            title = re.sub(r'[^\w^ ]', '', title)
            words = title.split(" ")
            initials = [word[0] for word in words]
            abr = "".join(initials)
            return abr

        raw_title = raw_title if raw_title else input("project title: ")
        safe_title = get_safe_title(raw_title)
        title_abr = get_title_abr(raw_title)
        TitleTracker = namedtuple('TitleTracker', ['raw', 'safe_for_path', 'abr'])
        return TitleTracker(raw=raw_title, safe_for_path=safe_title, abr=title_abr)


    def update_file_paths(self):
        """ Saves the paths to the various project files to the tracker """

        self.files.info = os.path.join(self.folder, f'{self.title.abr} info.yaml')
        self.files.template.dw = os.path.join(self.folder, f'{self.title.abr} dw.txt')
        self.files.template.ao3 = os.path.join(self.folder, f'{self.title.abr} ao3.csv')
        
        def get_files(contains="", endswith="", folder=self.folder):
            """ Looks for files in the given folder which name contains and ends with the
            given strings """
            files = [
                os.path.join(folder, file)
                for file in os.listdir(folder)
                if contains in file and file.endswith(endswith)
            ]
            return files

        self.files.audio.compressed.unformatted = get_files(self.title.abr, ".mp3")
        self.files.audio.raw.unformatted = get_files(self.title.abr, ".wav")
        self.files.audio.compressed.formatted = get_files(self.title.safe_for_path, ".mp3")
        self.files.audio.raw.formatted = get_files(self.title.safe_for_path, ".wav")
        self.files.cover.compressed = get_files(self.title.abr, ".png")
        self.files.cover.raw = get_files(self.title.abr, ".svg")
        self.files.fic = get_files(endswith=".html")
