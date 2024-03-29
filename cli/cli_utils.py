
from typing import Optional, Tuple
from src.ia_uploader import IAUploaderError
from src.project import Project, ProjectsTracker


def check_id(id:str, tracker:ProjectsTracker) -> str:
    """ If the ID is free, just returns it. If it's not, asks the user if that's okay, if not, asks for
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


def check_update_with_local_info(exception_message:str) -> bool:
    """ Project.get_project(id) can raise a FileNotFoundError in the case where the folder or metadata
    file have been moved
    Asks the user whether to load from project tracker only """
    print(exception_message)
    print("Do you want to:")
    print("- Use the tracker info only (input tracker then hit return)")
    print("- Quit (input quit then hit return)")
    print("- Try again (input nothing and hit return)")
    choice = input("Your choice? ")
    if choice == "quit": exit()
    elif choice == "tracker": return False
    else: return True



def get_existing_id_and_project(tracker:ProjectsTracker, id:Optional[str]=None,
    fandom:Optional[str]=None, title:Optional[str]=None, update_with_local_info:bool=True,
    verbose:bool=True) -> Tuple[str, Project]:
    """ """
    if id:
        id = check_id(id, tracker)
        try: project = tracker.get_project(id, update_with_local_info)
        except FileNotFoundError as e:
            return get_existing_id_and_project(
                tracker, id, fandom, title, verbose=verbose,
                update_with_local_info=check_update_with_local_info(e.message))
        return id, project
    print("No project ID?")
    print("- Use title and fandom instead (hit enter without typing anything")
    print("- Input a project ID (type then hit enter)")
    print("- Quit (type quit hit enter)")
    choice = input("Your choice? ")
    if choice == "quit": exit()
    elif choice != "":
        id = check_id(choice, tracker)
        try: project = tracker.get_project(id, update_with_local_info)
        except FileNotFoundError as e:
            return get_existing_id_and_project(
                tracker, id, fandom, title, verbose=verbose,
                update_with_local_info=check_update_with_local_info(e.message))
    else:
        fandom_abr = fandom if fandom else input("Fandom abr: ")
        raw_title = title if title else input("Full project title: ")
        project = Project(
            raw_title, fandom_abr, download_parent=False, reset_metadata=False, verbose=verbose)
        id = check_id(project.project_id.get_generic_id(), tracker)
    return id, project


def get_ia_id(error:IAUploaderError) -> Tuple[str, bool]:
    """ Returns IA item ID and overwrite parameter """
    print(error.message)
    print("Do you want to:")
    print("- Use this ID (hit return without typing anything)")
    print("- Input a new ID (type it then hit return)")
    print("- Quit (type quit then hit return)")
    choice = input("Your choice? ")
    if choice == "quit": exit()
    elif choice == "": return error.id, True
    else: return choice, False

def get_kpop_or_not() -> bool:
    """ Asks user if the podfic is kpop """
    print("Is this a kpop podfic and do you want to @ kpop_podfic?")
    print("- No (input nothing and hit return)")
    print("- Yes (input something then hit return)")
    print("- Quit (type quit then hit return)")
    choice = input("Your choice? ")
    if choice == "quit": exit()
    elif choice == "": return False
    else: return True
