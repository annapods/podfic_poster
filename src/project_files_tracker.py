# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" No main, don't run TODO test main? """

from os.path import join, exists
from os import mkdir, listdir
import sys
from src.base_object import VerboseObject


class CompressedFileTracker:
    """ Compressed and raw versions of the same file(s), ex: wav VS mp3 audio, or svg VS png cover
    art """
    def __init__(self, compressed=[], raw=[]):
        self.compressed = compressed
        self.raw = raw

class FormattedFileTracker:
    """ Formatted and unformatted versions of the same file(s), ex: mp3 file named after the
    project abbreviation, no metadata, no cover art VS ready to be posted """
    def __init__(self, formatted=[], unformatted=[]):
        self.formatted = formatted
        self.unformatted = unformatted

class TemplateFileTracker:
    """ Filled ao3 and dw template files """
    def __init__(self, ao3="", dw=""):
        self.ao3 = ao3
        self.dw = dw


class FileTracker(VerboseObject):
    """ Keeps track of project files:
    - folder
    - metadata
    - templates
        - ao3
        - dw
        - TODO add tracker?
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

    # Path to the parent folder of all the project folders
    wips_folder = "../../../Music/2.3 to post"
    # Path to the podfic tracker file, not yet implemented
    tracker = ""
    # Path to the DW file for accumulating podfics to xpost all at once
    dw_mass_xpost_file = join(wips_folder, "dw.txt")


    def __init__(self, project_id, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self.folder = self._get_folder()

        # Files which are always there, predictably named, etc
        self.metadata = join(self.folder, f'{self._project_id.title_abr} metadata.yaml')
        self.templates = TemplateFileTracker()
        self.templates.dw = join(self.folder, f'{self._project_id.title_abr} dw.txt')
        self.templates.ao3 = join(self.folder, f'{self._project_id.title_abr} ao3.csv')

        # Empty structure, will be filled by update_file_paths
        self.fic = []
        self.audio = CompressedFileTracker(FormattedFileTracker(), FormattedFileTracker())
        self.cover = CompressedFileTracker()
        self.update_file_paths()


    def update_file_paths(self):
        """ Populates the known files by looking for existing files in the folder """

        def get_files(contains:str="", endswith:str="", folder:str=self.folder):
            """ Looks for files in the given folder which name contains and ends with the
            given strings """
            files = [
                join(folder, file)
                for file in listdir(folder)
                if contains.lower() in file.lower() and file.endswith(endswith)
            ]
            return sorted(files)

        self.audio.compressed.unformatted = get_files(self._project_id.title_abr, ".mp3")
        self.audio.raw.unformatted = get_files(self._project_id.title_abr, ".wav")
        self.audio.compressed.formatted = get_files(self._project_id.safe_title, ".mp3")
        self.audio.raw.formatted = get_files(self._project_id.safe_title, ".wav")
        self.cover.compressed = get_files(self._project_id.title_abr, ".png")
        self.cover.raw = get_files(self._project_id.title_abr, ".svg")
        self.fic = get_files(endswith=".html")

        # print("title abr", self._project_id.title_abr)
        # print("full title", self._project_id.safe_title)
        # print("mp3 wip", self.audio.compressed.unformatted)
        # print("mp3 final", self.audio.compressed.formatted)
        # print("wav wip", self.audio.raw.unformatted)
        # print("wav final", self.audio.raw.formatted)
        # print("cover png", self.cover.compressed)
        # print("cover svg", self.cover.raw)
        # print("fic", self.fic)


    def _get_folder(self, folder:str=""):
        """ Returns the path to the project folder, ex: "wips_folder/fandom - project"
        Gets user input on whether to create or reuse a folder
        WARNING gotta do the title and fandom stuff first """

        folder = folder if folder else join(
            FileTracker.wips_folder,
            f"{self._project_id.fandom_abr.lower()} - {self._project_id.title_abr}"
        )

        # If the folder already exists...
        if exists(folder):
            print(f"\nFound a project folder! {folder}")
            print("You can:")
            print("- Use it (hit return without typing anything)")
            print("- Quit (type quit and then hit return)")
            print("- Use another folder (type the path to the folder then hit return)")
            choice = input("Your choice? ")
            if choice == "":
                return folder
            if choice == "quit":
                print("Bye!")
                sys.exit()
            return self._get_folder(choice)

        # If the folder doesn't exist...
        print(f"\nThat folder doesn't exist yet: {folder}")
        print("You can:")
        print("- Create it (hit return)")
        print("- Quit (type quit)")
        print("- Use another folder path (type it into the terminal")
        choice = input("Your choice? ")
        if choice == "":
            mkdir(folder)
            return folder
        if choice == "quit":
            print("Bye!")
            sys.exit()
        return self._get_folder(choice)
