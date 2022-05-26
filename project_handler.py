# -*- coding: utf-8 -*-
""" No main, don't run TODO test main? """

import re
from ao3_drafter import Ao3Poster
from audio_handler import AudioHandler
from dw_poster import DWPoster
from gdrive_uploader import GDriveUploader
from html_downloader import HTMLDownloader
from ia_uploader import IAUploader
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


class ProjectHandler:
    """ Keeps track of all project info:
    - id
    - metadata
    - files """

    def __init__(self, link:str="", fandom_abr:str="", raw_title:str="", mode:str="saved",
        verbose:bool=True):
        self._verbose = verbose
        self.id = ProjectID(fandom_abr, raw_title)
        self.files = FileTracker(self.id, verbose)

        if mode == "extract":
            # Downloading parent work html
            if not link:
                link = input("link to parent work(s): ")
            HTMLDownloader(verbose=verbose).download_html(link, self.files.folder)
            self.files.update_file_paths()

            # Extracting info from html
            self.metadata = ProjectMetadata(self, mode, verbose=verbose)

        elif mode == "saved":
            # Load data from saved file
            self.metadata = ProjectMetadata(self, mode, verbose)

        else:
            assert False, "Mode must be 'extracted' or 'saved'."


    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def post(self):
        """ Posting everything.
        /!\\ everything has to be ready, will fail otherwise """
        # Adding posting date to metadata
        self.metadata.add_posting_date()

        # Editing audio files for names and metadata
        audio = AudioHandler(self, verbose=self._verbose)
        audio.rename_wip_audio_files()
        audio.add_cover_art()
        audio.update_metadata()
        audio.save_audio_length()
        self.files.update_file_paths()

        # Uploading to gdrive
        gdrive_uploader = GDriveUploader(self, verbose=self._verbose)
        gdrive_uploader.upload_audio()
        gdrive_uploader.upload_cover()
        gdrive_uploader.upload_metadata()

        # Uploading to the internet archive
        ia_uploader = IAUploader(self, verbose=self._verbose)
        ia_uploader.upload_audio()
        ia_uploader.upload_cover()
        ia_uploader.upload_metadata()

        # Drafting ao3 post
        ao3_poster = Ao3Poster(self, verbose=self._verbose)
        ao3_poster.draft_podfic()

        # Uploading ao3 info to gdrive and ia
        gdrive_uploader.upload_metadata()
        ia_uploader.update_description()
        ia_uploader.upload_metadata()

        # Posting to dw
        dw_poster = DWPoster(self, verbose=self._verbose)
        dw_poster.save_dw_post_text()

        # Saving tracker info
        self.save_tracker_info()


    def save_tracker_info(self):
        """ TODO... """
        pass
        # self._vprint('saving tracker info...', end=" ")
        # self._vprint('done!')
