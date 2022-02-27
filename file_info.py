# -*- coding: utf-8 -*-

import os, re


class FileInfo:
    """ Keeps track of the project files
    fandom: fandom abbreviation TODO taxonomy
    title: name of the story
    project: title initials
    folder: path to the project folder """

    wips_folder = "../../../Musique/2.5 to post"

    def __init__(self, fandom="", title="", folder="", verbose=True):
        """ Any info left empty will be infered or asked in the command line interface """

        self.verbose = verbose
        self.fandom = fandom if fandom else input("fandom abr: ")
        self.title = title if title else input("project title: ")
        self.safe_title = self.get_safe_title()
        self.project = self.get_project()
        self.folder = folder if folder else self.get_folder()

        # Check that the folder exists
        if os.path.exists(self.folder):
        # If yes, ask for confirmation
            if input(f"use existing folder {self.folder}? nothing for yes"):
        # If asked to, create another folder
                self = FileInfo(fandom=self.fandom, title=self.title, folder=self.folder+" 2")
        # NOTE the duplicate naming scheme is simplistic and doesn't really hold up

        # If the folder doesn't exist, offer to create it
        else:
            print("/!\\ that folder doesn't exist yet")
            choice = input("create it? nothing for yes, quit for quit, whatever else to go back")
            if not choice:
                os.mkdir(self.folder)
        # Or quit
                if choice == "quit":
                    quit()
        # Or go back and input another fandom and project abreviation
            else:
                self = FileInfo(verbose=verbose)
        
        self.update_file_paths()


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def get_safe_title(self):
        """ Returns a version of the title that is safe for paths """
        title = self.title
        title = title.replace(".", ",")
        title = title.replace("/", " ")
        return title


    def get_project(self):
        """ Returns the project abbreviation, created from the title initials """
        title = self.title.lower()
        words = title.split(" ")
        initials = [word[0] for word in words]
        project = "".join(initials)
        return project


    def get_folder(self):
        """ Returns the path to the project folder, ex: "wips_folder/fandom - project" """
        return os.path.join(FileInfo.wips_folder, f"{self.fandom} - {self.project_abr}")
        

    def update_file_paths(self):
        """ Looks for files and saves the paths in object attributes """
        self.mp3_wips = self.get_files(contains=self.project, endswith=".mp3")
        self.wav_wips = self.get_files(contains=self.project, endswith=".wav")
        self.mp3_finals = self.get_files(endswith=".mp3")
        self.wav_finals = self.get_files(endswith=".wav")
        self.pngs = self.get_files(contains=self.project, endswith=".png")
        self.svgs = self.get_files(contains=self.project, endswith=".svg")
        self.html_fics = self.get_files(endswith=".html")
        self.dw = os.path.join(self.folder, f'{self.project} dw.txt')
        self.ao3 = os.path.join(self.folder, f'{self.project} ao3.csv')
        self.yaml_info = os.path.join(self.folder, f'{self.project} info.yaml')

    def get_files(self, contains="", endswith=".mp3"):
        """ Looks for files which name contains and ends with the given strings """
        files = [
            os.path.join(self.folder, file)
            for file in os.listdir(self.folder)
            if re.match(f".*{contains}.*{endswith}$", file)
        ]
        return files
