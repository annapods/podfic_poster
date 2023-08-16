# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from src.project_id import ProjectID
from src.ao3_drafter import Ao3Poster
from src.audio_handler import AudioHandler
from src.dw_poster import DWPoster
from src.gdrive_uploader import GDriveUploader
from src.html_downloader import HTMLDownloader
from src.ia_uploader import IAUploader
from src.project_files_tracker import FileTracker
from src.project_metadata import ProjectMetadata


if __name__ == "__main__":
    parser = ArgumentParser(description="Podfic posting helper!")
    parser.add_argument('mode', help="new or post?", choices=['new', 'post'])
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    parser.add_argument('--link', help="link to the ao3 work", default=None)
    parser.add_argument('--fandom', help="abreviation of the fandom " + \
        "(like at the start of the mp3 file name)", default=None)
    parser.add_argument('--title', help="title of the work", default=None)
    args = parser.parse_args()

    verbose = not args.quiet
    project_id = ProjectID(fandom_abr=args.fandom, raw_title=args.title)
    files = FileTracker(project_id, verbose)

    if args.mode == "new":
        # Downloading parent work html
        link = args.link if args.link else input("Link to parent work(s), input nothing to skip: ")

        if link:
            HTMLDownloader(verbose=verbose).download_html(link, files.folder)
            files.update_file_paths()

            # Extracting info from html
            metadata = ProjectMetadata(files, mode="from html", verbose=verbose)

        else:
            metadata = ProjectMetadata(files, mode="from scratch", verbose=verbose)

    if args.mode == "post":
        metadata = ProjectMetadata(files, mode="from yaml", verbose=verbose)

        # Adding posting date to metadata
        metadata.add_posting_date()

        # Editing audio files for names and metadata
        audio = AudioHandler(project_id, files, metadata, verbose)
        audio.rename_wip_audio_files()
        audio.add_cover_art()
        audio.update_metadata()
        audio.save_audio_length()
        files.update_file_paths()

        # Uploading to gdrive
        gdrive_uploader = GDriveUploader(project_id, files, metadata, verbose)
        gdrive_uploader.upload_audio()
        gdrive_uploader.upload_cover()

        # Uploading to the internet archive
        ia_uploader = IAUploader(project_id, files, metadata, verbose)
        ia_uploader.upload_audio()
        ia_uploader.upload_cover()

        # Drafting ao3 post
        ao3_poster = Ao3Poster(project_id, files, metadata, verbose)
        ao3_poster.draft_podfic()

        # Uploading project info to gdrive and ia
        gdrive_uploader.upload_metadata()
        ia_uploader.update_description()
        ia_uploader.upload_metadata()

        # Posting to dw
        dw_poster = DWPoster(project_id, files, metadata, verbose)
        dw_poster.save_dw_post_text()

        # # Saving tracker info
        # ??.save_tracker_info()
