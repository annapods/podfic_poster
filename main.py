# -*- coding: utf-8 -*-
"""
Command line program (TODO)
"""

from argparse import ArgumentParser
from html_downloader import HTMLDownloader
from audio_handler import AudioHandler
from work_info import WorkInfo
from file_info import FileInfo
from gdrive_uploader import GDriveUploader
from ia_uploader import IAUploader
from ao3_poster import Ao3Poster
from dw_poster import DWPoster


TEST_URL = "https://archiveofourown.org/works/35806393"


def new(link=TEST_URL, verbose=True):
    """ Setting up the posting stuff:
    - downloading html
    - extracting data from it
    - creating a few files """
    files = FileInfo(fandom='hrpf', project='nbsldmstjf', verbose=verbose)

    # Downloading parent work html
    if not link:
        link = input("link to parent work(s): ")
    HTMLDownloader(verbose=verbose).download_html(link, files.folder)
    files.update_file_paths()

    # Extracting info from html
    work = WorkInfo(files, mode="extract", verbose=verbose)
    work.save_info()


def post(verbose=True):
    """ Posting everything.
    /!\\ everything has to be ready, will fail otherwise """
    # Extracting info from files
    files = FileInfo(fandom="test", project="test", verbose=verbose)
    work = WorkInfo(files, mode="saved", verbose=verbose)

    # Editing audio files for names and metadata
    audio = AudioHandler(files, work, verbose=verbose)
    audio.add_cover_art()
    audio.rename_wip_audio_files()
    audio.update_metadata()
    audio.save_audio_length()

    # Uploading to gdrive and ia
    gdrive_uploader = GDriveUploader(files, work, verbose=verbose)
    gdrive_uploader.upload_audio()
    gdrive_uploader.upload_cover()
    ia_uploader = IAUploader(files, work, verbose=verbose)
    ia_uploader.upload_audio()
    ia_uploader.upload_cover()

    # Posting to ao3
    work.create_ao3_template()
    ao3_poster = Ao3Poster(files, work, verbose=verbose)
    ao3_poster.post_podfic()

    # Uploading ao3 info to gdrive and ia
    gdrive_uploader.upload_info()
    ia_uploader.update_description()
    ia_uploader.upload_info()

    # Posting to dw
    work.create_dw_template()
    dw_poster = DWPoster(files, work, verbose=verbose)
    dw_poster.post_podfic()

    # Saving tracker info
    work.save_tracker_info()


if __name__ == "__main__":
    parser = ArgumentParser(description="Podfic posting helper!")
    parser.add_argument('mode', help="new or post?", choices=['new', 'post'])
    parser.add_argument('--verbose', '-v', help="verbose mode",
        action='store_true', required=False)
    args = parser.parse_args()

    verbose = args.verbose

    if args.mode == "new":
        new(verbose=verbose)

    if args.mode == "post":
        post(verbose=verbose)
