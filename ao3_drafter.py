# -*- coding: utf-8 -*-
""" TODO main test """

# import pexpect
import json
from ao3_poster.ao3 import login, logout, post
from csv import DictReader


class Ao3Poster:
    """ Ao3 posting helper!
    Uses ao3-poster to create an ao3 draft
    https://ao3-poster.readthedocs.io/en/latest/index.html """

    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = project_info
        self._work = work_info

    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def _get_session(self):
        """ Fetches credentials and logs in to an ao3 session. """
        self._vprint("Loging in to ao3...", end=" ")

        # Ao3 credentials should be saved in the settings file
        with open("settings.json", "r") as file:
            settings = json.load(file)
            # However, if they're not (yet), we don't want an error either, hence the get
            username = settings.get("username", "")
            password = settings.get("password", "")

        # login will return a session if succesful, and None otherwise
        session = login(username, password)
        if session:
            return session

        # If it fails, we assume it's because the credentials were wrong
        # Though tbh that's a strong assumption

        # We ask for new credentials, taking care not to erase the other info that might
        # already be in the file by completely overwriting it
        settings["username"] = input("ao3 username? ")
        settings["password"] = input("ao3 password? ")

        # We save the credentials
        with open("settings.json", 'w') as file:
            json.dump(settings, file)

        # And we try again
        return self._get_session()


    def draft_podfic(self):
        """ Drafts the ao3 post!
        Assuming that we're creating one draft at a time, so we're opening and closing the
        session at each call. """
        self._vprint("Drafting podfic post to ao3...", end=" ")

        # Get session
        session = self._get_session()

        # Get work post info
        reader = DictReader(self._project.files.template.ao3)
        rows = list(reader)

        # Create post
        link = post(session, rows[0], work_text_template=None)
        # TODO (potentially): the ao3-poster code isn't that long, and includes yet another
        # reformatting from the required csv template to some other data structure. Could be
        # more convenient to go directly from our yaml structure to what is needed for posting?

        # Log out afterward
        logout(session)

        # Save the link to the project info
        self._work.update_info(category="Podfic Link", content=link)

        self._vprint("done!\n")



# #  Code for drafting using the ao3-poster command line interface
# #  Uses pexpect to interact with the cli, not ideal
# #  https://pexpect.readthedocs.io/en/stable/overview.html?highlight=before#api-overview
# cmd = f"ao3 post '{self._project.files.template.ao3}"
# with pexpect.spawn(cmd) as process:
#     process.expect('Username or email:')
#     process.sendline(username)
#     process.expect('Password:')
#     process.sendline(password)
#     process.expect('Repeat for confirmation:')
#     process.sendline(password)
#     time.sleep(5)
#     process.expect('https:.*/[0-9]+')
#     link = process.after.decode('utf-8')
