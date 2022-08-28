# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" TODO main test """

# import pexpect
import json
# from csv import DictReader
from ao3_poster.ao3 import login, logout, post

from template_filler import Ao3Template
from base_object import VerboseObject


class Ao3Poster(VerboseObject):
    """ Ao3 posting helper!
    Uses ao3-poster to create an ao3 draft
    https://ao3-poster.readthedocs.io/en/latest/index.html """

    def __init__(self, project_id, files, metadata, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self._files = files
        self._metadata = metadata

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

        # Get data
        data = self._get_ao3_data()

        # Get session
        session = self._get_session()

        # Create post
        link = post(session, data, work_text_template=None)
        # TODO (potentially): the ao3-poster code isn't that long, and includes yet another
        # reformatting from the required csv template to some other data structure. Could be
        # more convenient to go directly from our yaml structure to what is needed for posting?

        # Log out afterward
        logout(session)

        # Save the link to the project info
        self._metadata.update_md(category="Podfic Link", content=link)

        self._vprint("done!\n")


    def _get_ao3_data(self):
        """ Creates ao3 posting data dict according to ao3-poster format, using Ao3Template to
        format body and summary of the post """
        self._vprint('Creating ao3 template...', end=" ")
        metadata = self._metadata  # just for convenience, bc it's pretty long...
        metadata.check_and_format(posted=False)
        metadata.add_podfic_tags()

        template = Ao3Template(self._metadata)
        metadata.update_md("Summary", template.summary)
        metadata.update_md("Work text", template.work_text)

        data = {}
        data["Work Title"] = f'[{metadata["Work Type"]}] ' + \
            f'{self._project_id.raw_title}'

        for key in ["Fandoms", "Relationships",
            "Characters", "Additional Tags", "Archive Warnings", "Categories"]:
            data[key] = ", ".join(metadata[key])

        for key in ["Creator/Pseud(s)", "Add co-creators?"]:
            if metadata[key]:
                pseuds = [pseud for _, pseud in metadata[key] if not pseud.startswith("__")]
                data[key] = ", ".join(pseuds)

        for key in ["Summary", "Notes at the beginning", "Notes at the end", "Language",
            "Work text", "Parent Work URL", "Rating"]:
            data[key] = metadata[key]

        if isinstance(metadata["Parent Work URL"], list) \
            and len(metadata["Parent Work URL"]) > 0:
            data["Parent Work URL"] = data["Parent Work URL"][0]
        else:
            data["Parent Work URL"] = ""

        return data


# #  Code for drafting using the ao3-poster command line interface
# #  Uses pexpect to interact with the cli, not ideal
# #  https://pexpect.readthedocs.io/en/stable/overview.html?highlight=before#api-overview
# cmd = f"ao3 post '{self._files.template.ao3}"
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
