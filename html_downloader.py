# -*- coding: utf-8 -*-y
""" Uses ao3downloader https://github.com/nianeyna/ao3downloader """

import requests

import ao3downloader.actions.globals as globals
import ao3downloader.ao3 as ao3
import ao3downloader.fileio as fileio
from ao3downloader.strings import DOWNLOAD_FOLDER_NAME


class HTMLDownloader:
    """ Download parent work html from ao3 to the destination folder """

    def __init__(self, verbose=True):
        self.verbose = verbose


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def download_html(self, link, folder):
        """ Downloading! 
        Edited from ao3downloader/actions/ao3download.py """

        self.vprint("Downloading html...")
        session = requests.sessions.Session()
        globals.ao3_login(session, login=True)
        logfile = globals.get_logfile(DOWNLOAD_FOLDER_NAME)
        fileio.write_log(logfile, {'starting': link})
        filetype = "HTML"
        subfolders = False
        pages = 0
        ao3.download(link, filetype, folder, logfile, session, subfolders, pages)
        session.close()
        self.vprint("...done!")
