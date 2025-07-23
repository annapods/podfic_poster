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
    # ("", "", "")
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
    # # Battleship
    # ("B", "The Teahouse", None),
    # ("SK8", "Slippery Slope", None),
    # ("N", "It's not time that passes", None),
    # ("SVSSS", "Omne Trium Perfectum", None),
    # ("SCTIR", "Ready, set, go", None),
    # ("DCU", "What Happens in the Horsehead Nebula (gets recreated by Roy later)", None),
    # ("Orig", "Mike's Hard Lemonade", None),
    # ("Orig", "Collecting Empirical Data of Primary Sex Characteristics of Merfolk in the Pacific North West", None),
    # ("DCU", "The looping of the line", None),
    # ("DCU", "The Snowball Effect", None),
    # ("DCU", "A kingdom molten", None),
    # ("Orig", "Dammed If I Do, Dammed If I Don't", None),
    # ("N", "Seven New Ways", None),
    # ("Orig", "Refuge", None),
    # ("DCU", "dark blue land mine", None),
    # ("DCU", "when the sun sets, we’re both the same", None),
    # ("KPDM", "sinking under it all", None),
    # ("N", "all our troubles (home to roost)", None),
    # ("DCU", "their records kept here undefiled", None),
    # ("BNHA", "though the embers are new", None),
    # ("Orig", "to sing through the storm", None),
    # ("Orig", "The Unhaunted House", None),
    # ("Orig", "Companion?", None),
    # ("Orig", "Wanna Bet?", None),
    # ("SCTIR", "A quarterly... vacation?", None),
    # ("SCTIR", "night light", None),
    # ("N", "If set in stone (reverse)", None),
    # ("KPDM", "Tonight we can write lines of gold", None),
    # ("Orig", "The Thief", None),
    # ("Orig", "Displeased", None),
    # ("Orig", "Things I Have Been", None),
    # ("N", "Like a pebble in the current", None),
    # ("Orig", "Notes On My Stay With The Green Cavern Dwarves", None),
    # ("Sk8", "Blue Balls and Bragging Rights", None),
    # ("Orig", "ballad of the wonderbloom", None),
    # ("AS", "HOW TO DEAL WITH GRIEF, a comprehensive guide", None),
    # ("Orig", "Icebreaker", None),
    # ("AtlA", "Scales of Embers, None")
    # ("BNHA", "Nothing but sparks and glitter", None),
    # ("Orig", "Those New Mistakes", None),
    # ("GI", "Initial Data Collection", None),
    # ("SH", "what did I come down here for?", None),
    # ("Orig", "seven new ways to eat your young", None),
    # ("BNHA", "A Double Dose of Deku", None),
    # ("DM", "FUCKOYAKI", None),
    # ("BNHA", "The Other Side of Us", None),

    # # Podfic Summer Swap
    # ("SVSSS", "It's you I find like a ghost in my mind", "https://archiveofourown.org/works/52525798"),
]
for fandom, title, _ in to_promo:
    project = Project(title, fandom, None, download_parent=False, reset_metadata=False, verbose=verbose)
    # Drafting dw post
    dw_poster = DWPoster(project, verbose)
    dw_poster.save_dw_post_text()
    # Promoting on tumblr
    tumblr_poster = TumblrPoster(project, verbose)
    tumblr_poster.post_promo()


