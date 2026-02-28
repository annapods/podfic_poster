# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from sys import exit

from src.project import Project, ProjectsTracker


def get_id(id:str, tracker:ProjectsTracker) -> str:
    """ If the ID is fjree, just returns it. If it's not, asks the user if that's okay, if not, asks for
    a new ID """
    keep_going = True
    while keep_going and tracker.id_exists(id):
        print(f"\nProject ID {id} already exists. Do you want to:")
        print("- Use it (hit return without typing anything)")
        print("- Input a new ID (type the ID then hit return)")
        print("- Quit (type quit then hit return)")
        choice = input("Your choice? ")
        if choice == "quit": exit()
        elif choice == "": keep_going = False
        else: id = choice
    return id


def setup(project:Project) -> None:
    pass

if __name__ == "__main__":
    parser = ArgumentParser(prog="Podfic project setup!", description="Use once all the files are ready")
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    parser.add_argument('--link', help="link to the ao3 work for download", default=None)
    parser.add_argument('--fandom', help="abreviation of the fandom " + \
        "(like at the start of the mp3 file name)", default=None)
    parser.add_argument('--title', help="title of the work", default=None)
    parser.add_argument('--id', help="id of the project", default=None)
    args = parser.parse_args()

    verbose = not args.quiet
    tracker = ProjectsTracker(tracker_path="/home/anna/Music/tracker.json", verbose=verbose)

    fandom_abr = args.fandom if args.fandom else input("Fandom abr: ")
    raw_title = args.title if args.title else input("Full project title: ")
    link = args.link if args.link else input(
        "Link to parent work(s), input nothing to skip and not overwrite any metadata: ")

    link_given = link is not None
    reset_metadata = link_given

    try:
        project = Project(raw_title, fandom_abr, link, download_parent=False, reset_metadata=True,
            verbose=verbose)
    except FileNotFoundError:
        project = Project(raw_title, fandom_abr, link, download_parent=link_given, reset_metadata=True,
            verbose=verbose)
    id = get_id(project.project_id.get_generic_id(), tracker)
    tracker.update_project(id, project, overwrite=True)
    print("\nSetup", id)
