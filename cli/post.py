# -*- coding: utf-8 -*-
""" Command line program to post a podfic """

from argparse import ArgumentParser
from traceback import print_exc
from src.project_metadata import placeholder_text
from src.ao3_drafter import ao3_draft, drafted
from src.audio_handler import AudioHandler
from src.gdrive_uploader import GDriveUploader
from src.ia_uploader import IAUploader, IAUploaderError
from src.project import Project, ProjectsTracker
from cli.cli_utils import get_existing_id_and_project, get_ia_id


def handle_ao3_draft_errors(e:Exception, cooldown:int=60) -> None:
    """ Prints details if not SSL handshake error, sleeps for cooldown seconds """
    if "525" in str(e): print(f"SSL ERROR ENCOUNTERED - will try again in {cooldown}")
    else:
        print(f"ERROR ENCOUNTERED - will try again in {cooldown} - {e}")
        print_exc()

def load_ia_project(ia:IAUploader, project:Project, force_ia_id:bool) -> None:
    try: ia.load_project(project, None, force_ia_id)
    except IAUploaderError as e:
        ia_id, overwrite = get_ia_id(e)
        ia.load_project(project, ia_id, overwrite)

def post(
        tracker:ProjectsTracker, project:Project, gd:GDriveUploader,
        ia:IAUploader, audio:AudioHandler,
        max_ao3_drafting_attempts:int, downtime:int, force_ia_id, verbose:bool) -> None:
    
    # Adding posting date to metadata
    project.metadata.add_posting_date()

    # Editing audio files for names and metadata
    audio.load_project(project)
    audio.rename_wip_audio_files()
    audio.add_cover_art()
    audio.update_metadata()
    audio.save_audio_length()

    # Uploading to gdrive
    if placeholder_text(project.metadata.get("GDrive Link")):
        gd.load_project(project)
        gd.upload_audio()
        gd.upload_cover()
    tracker.update_project(id, project, overwrite=True)

    # Uploading to the internet archive
    if placeholder_text(project.metadata.get("IA Link")):
        load_ia_project(ia, project, force_ia_id)
        ia.upload_compressed_audio()
        ia.upload_raw_audio()
        ia.upload_cover()
    tracker.update_project(id, project, overwrite=True)

    # Drafting ao3 post, trying several times in case of SSL handshake error
    if not drafted(project):
        ao3_draft(
            project, max_ao3_drafting_attempts,
            handle_ao3_draft_errors, downtime, verbose)
        tracker.update_project(id, project, overwrite=True)

    # Uploading project info to gdrive and ia
    if drafted(project):
        gd.load_project(project)
        gd.upload_metadata()
        load_ia_project(ia, project, force_ia_id)
        ia.update_description()
        ia.upload_metadata()



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

    gd = GDriveUploader()
    ia = IAUploader()
    audio = AudioHandler()

    max_ao3_drafting_attempts = 15
    downtime = 60

    print("\Posting", id)
    post(project, gd, ia, audio, max_ao3_drafting_attempts, downtime, False, verbose)
    # Saving tracker info
    tracker.update_project(id, project, overwrite=True)
