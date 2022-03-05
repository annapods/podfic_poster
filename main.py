# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from html_downloader import HTMLDownloader
from audio_handler import AudioHandler
from posting_info import WorkInfo
from project_tracker import ProjectTracker
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
    project = ProjectTracker(fandom='hrpf',
        title="NYT Best Seller List Don't Mean Shit (To Joel Farabee)",
        verbose=verbose)

    # Downloading parent work html
    if not link:
        link = input("link to parent work(s): ")
    HTMLDownloader(verbose=verbose).download_html(link, project.folder)
    project.update_file_paths()

    # Extracting info from html
    WorkInfo(project, mode="extract", verbose=verbose)


def post(verbose=True):
    """ Posting everything.
    /!\\ everything has to be ready, will fail otherwise """
    # Extracting info from files
    project = ProjectTracker(fandom='hrpf',
        title="NYT Best Seller List Don't Mean Shit (To Joel Farabee)",
        verbose=verbose)
    work = WorkInfo(project, mode="saved", verbose=verbose)

    # Editing audio files for names and metadata
    audio = AudioHandler(project, work, verbose=verbose)
    # audio.add_cover_art()
    # audio.rename_wip_audio_files()
    # audio.update_metadata()
    # audio.save_audio_length()
    # project.update_file_paths()

    # Uploading to gdrive and ia
    # gdrive_uploader = GDriveUploader(project, work, verbose=verbose)
    # gdrive_uploader.upload_audio()
    # gdrive_uploader.upload_cover()
    # ia_uploader = IAUploader(project, work, verbose=verbose)
    # ia_uploader.upload_audio()
    # ia_uploader.upload_cover()

    # Posting to ao3
    work.create_ao3_template()
    ao3_poster = Ao3Poster(project, work, verbose=verbose)
    ao3_poster.post_podfic()

    # # Uploading ao3 info to gdrive and ia
    # gdrive_uploader.upload_info()
    # ia_uploader.update_description()
    # ia_uploader.upload_info()

    # Posting to dw
    work.create_dw_template()
    dw_poster = DWPoster(project, work, verbose=verbose)
    dw_poster.post_podfic()

    # Saving tracker info
    work.save_tracker_info()


if __name__ == "__main__":
    parser = ArgumentParser(description="Podfic posting helper!")
    parser.add_argument('mode', help="new or post?", choices=['new', 'post'])
    parser.add_argument('--verbose', '-v', help="verbose mode",
        action='store_true', required=False)
    args = parser.parse_args()

    verbose = True  # args.verbose  # TODO change

    if args.mode == "new":
        new(verbose=verbose)

    if args.mode == "post":
        post(verbose=verbose)
