# -*- coding: utf-8 -*-
""" """

from cli.setup import get_id
from src.ia_uploader import IAUploader
from src.project import Project, ProjectsTracker
from src.audio_handler import AudioHandler
from src.dw_poster import DWPoster
from src.gdrive_uploader import GDriveUploader
from src.tumblr_poster import TumblrPoster
from cli.post import post





# paths = ["/home/anna/Music/tracker old 1.json", "/home/anna/Music/tracker old 2.json"]

# tracker_old_1 = ProjectsTracker(tracker_path=paths[0], verbose=True)
# tracker_old_2 = ProjectsTracker(tracker_path=paths[1], verbose=True)



verbose = True
tracker = ProjectsTracker(tracker_path="/home/anna/Music/tracker.json", verbose=verbose)


to_setup = [
    # ("", "", ""),
]
for fandom, title, link in to_setup:
    project = Project(title, fandom, link, download_parent=True, reset_metadata=True, verbose=verbose)
    id = get_id(project.project_id.get_generic_id(), tracker)
    tracker.update_project(id, project, overwrite=True)
    print("Setup", id, "done!")


to_post = [
]
if to_post:
    gd = GDriveUploader()
    ia = IAUploader()
    audio = AudioHandler()
    max_ao3_drafting_attempts = 20
downtime = 180
for fandom, title, _ in to_post:
    project = Project(title, fandom, None, download_parent=False, reset_metadata=False, verbose=verbose)
    id = project.project_id.get_generic_id()
    tracker.update_project(id, project, overwrite=True)
    post(
        tracker, project, gd, ia, audio, max_ao3_drafting_attempts,
        downtime, True, verbose)
    tracker.update_project(id, project, overwrite=True)


to_promo = [
]
# from cli.post import load_ia_project
# from multiprocessing import Process
# from time import sleep
# timeout = 60
# timed = 4
# ia = IAUploader()

for fandom, title, _ in to_promo:
    project = Project(title, fandom, None, download_parent=False, reset_metadata=False, verbose=verbose)
    id = project.project_id.get_generic_id()
    # Drafting dw post
    dw_poster = DWPoster(project, verbose)
    dw_poster.save_dw_post_text()
    # Promoting on tumblr
    tumblr_poster = TumblrPoster(project, verbose)
    tumblr_poster.post_promo()

    # # Uploading raw file to the internet archive
    # load_ia_project(ia, project, force_ia_id=True)
    # process = Process(target=ia.upload_raw_audio)
    # process.start()
    # for i in range(timed):
    #     if process.is_alive():
    #         print("Loading...")
    #         sleep(timeout)
    #     else: print("Loaded raw file for "+title)
    # # process.join()
    # if process.is_alive():
    #     process.kill()
    #     print("Failed to load raw file for "+title)



