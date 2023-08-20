# -*- coding: utf-8 -*-
""" Command line program to post a podfic """

from argparse import ArgumentParser
from src.ao3_drafter import Ao3Poster
from src.audio_handler import AudioHandler
from src.gdrive_uploader import GDriveUploader
from src.ia_uploader import IAUploader
from src.project import ProjectsTracker
from cli.cli_utils import get_existing_id_and_project


if __name__ == "__main__":
    parser = ArgumentParser(prog="Podfic project posting!", description="Use once metadata is ready")
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    parser.add_argument('--link', help="link to the ao3 work", default=None)
    parser.add_argument('--fandom', help="abreviation of the fandom " + \
        "(like at the start of the mp3 file name)", default=None)
    parser.add_argument('--title', help="title of the work", default=None)
    parser.add_argument('--id', help="id of the project", default=None)
    args = parser.parse_args()

    verbose = not args.quiet
    tracker = ProjectsTracker(tracker_path="/home/anna/Music/tracker.json", verbose=verbose)
    id, project = get_existing_id_and_project(tracker, args.id, args.fandom, args.title, verbose)
    tracker.update_project(id, project, overwrite=True)
    print("\nProject ID:", id)

    # Adding posting date to metadata
    project.metadata.add_posting_date()

    # Editing audio files for names and metadata
    # TODO !!!! project_id, files and metadata -> project
    audio = AudioHandler(project)
    audio.rename_wip_audio_files()
    audio.add_cover_art()
    audio.update_metadata()
    audio.save_audio_length()

    # Uploading to gdrive
    gdrive_uploader = GDriveUploader(project)
    gdrive_uploader.upload_audio()
    gdrive_uploader.upload_cover()

    # Uploading to the internet archive
    ia_uploader = IAUploader(project)
    ia_uploader.upload_audio()
    ia_uploader.upload_cover()

    # Drafting ao3 post
    ao3_poster = Ao3Poster(project, verbose)
    ao3_poster.draft_podfic()

    # Uploading project info to gdrive and ia
    gdrive_uploader.upload_metadata()
    ia_uploader.update_description()
    ia_uploader.upload_metadata()

    # Saving tracker info
    tracker.update_project(id, project, overwrite=True)
