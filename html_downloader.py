# -*- coding: utf-8 -*-y

import os
import json
import shutil
from ao3downloader.actions.ao3download import action as ao3download
from ao3downloader.strings import DOWNLOAD_FOLDER_NAME, LOG_FILE_NAME
from ao3downloader.fileio import get_valid_filename


class HTMLDownloader:
    """ Download parent work html from ao3 to the destination folder 
    Wrapping up ao3downloader, mostly, with some additional file moving """
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.log_file = os.path.join(DOWNLOAD_FOLDER_NAME, LOG_FILE_NAME)
        self.logs = []
        self.file_names = []


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def get_log(self):
        """ Using logfile to get back the log, deleting it afterward
        /!\ That means you can't use it twice (TODO that might be a bad idea...) """
        assert not self.logs, "/!\\ already loaded log!"
        with open(self.log_file, 'r') as json_file:
            self.logs = list(json_file)
        os.remove(self.log_file)


    def get_file_names(self):
        """ Get the names of the html files from the log """
        self.file_names = []
        for log in self.logs:
            log = json.loads(log)
            if "starting" not in log:
                self.vprint(log)
                title = get_valid_filename(log['title'])
                self.file_names.append(f"{title}.html")
        return self.file_names


    def move_html_files(self, folder, download_folder=DOWNLOAD_FOLDER_NAME):
        """ Moves the html files to the pod folder """
        for file_name in self.file_names:
            work_file = os.path.join(download_folder, file_name)
            shutil.move(work_file, os.path.join(folder, file_name))


    def download_html(self, link, destination_folder):
        """ Pipeline! """
        self.vprint("Downloading html...")
        ao3download(link=link, filetype='HTML', subfolders=False, pages=0, login=True)
        self.get_log()
        self.get_file_names()
        self.move_html_files(destination_folder)
        self.vprint("...done!")
