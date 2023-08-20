# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-y
""" Uses ao3downloader https://github.com/nianeyna/ao3downloader """

import requests

from ao3downloader.actions import globals as ao3dl_globals
from ao3downloader import ao3, fileio
from ao3downloader.repo import login
from ao3downloader.strings import DOWNLOAD_FOLDER_NAME
from src.base_object import BaseObject
from src.secret_handler import get_secrets

class HTMLDownloader(BaseObject):
    """ Download parent work html from ao3 to the destination folder """


    def download_html(self, link:str, folder:str):
        """ Downloading! Edited from ao3downloader/actions/ao3download.py """

        self._vprint("\nDownloading html...")
        session = requests.sessions.Session()
        username, password = get_secrets(["ao3_username", "ao3_password"])
        login(username, password, session)
        logfile = ao3dl_globals.get_logfile(DOWNLOAD_FOLDER_NAME)
        fileio.write_log(logfile, {'starting': link})
        filetype = "HTML"
        subfolders = False
        pages = 0
        ao3.download(link, filetype, folder, logfile, session, subfolders, pages)
        session.close()
        self._vprint("Done!\n")
