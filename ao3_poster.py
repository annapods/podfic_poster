# -*- coding: utf-8 -*-
""" TODO main test """

import pexpect
import json
import time


class Ao3Poster:
    """ Ao3 posting helper!
    Uses ao3-poster to create the draft, and pexpect to interact with ao3-poster
    https://pexpect.readthedocs.io/en/stable/overview.html?highlight=before#api-overview """

    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = project_info
        self._work = work_info

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def post_podfic(self):
        """ TODO """
        self._vprint("Drafting podfic post to ao3...", end=" ")

        with open("settings.json", "r") as file:
            settings = json.load(file)
            username = settings["username"]+'\n'
            password = settings["password"]+'\n'

        cmd = f"ao3 post '{self._project.files.template.ao3}"
        with pexpect.spawn(cmd) as process:
            process.expect('Username or email:')
            process.sendline(username)
            process.expect('Password:')
            process.sendline(password)
            process.expect('Repeat for confirmation:')
            process.sendline(password)
            time.sleep(5)
            process.expect('https:.*/[0-9]+')
            link = process.after.decode('utf-8')

        self._work.update_info(category="Podfic Link", content=link)
        print(self._work.info["Podfic Link"])
        self._vprint("done!\n")
