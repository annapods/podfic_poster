# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
""" No main, don't run TODO test main? """

import re


class ProjectID:
    """ Keeps track of project id details:
    - id
    - fandom_abr
    - raw_title
    - safe_title
    - title_abr
    - full_safe_title
    - full_raw_title

    Used by ProjectTracker """

    def __init__(self, fandom_abr:str, raw_title:str) -> None:
        self.fandom_abr, self.raw_title = fandom_abr, raw_title
        self.safe_title = self._get_safe_title(self.raw_title)
        self.title_abr = self._get_title_abr()
        self.full_safe_title = self._get_full_title(safe_for_path=True)
        self.full_raw_title = self._get_full_title(safe_for_path=False)

    def _get_safe_title(self, original:str):
        """ Returns a version of the title that is safe for paths
        If that is not the original, will ask, since there are so many different cases """
        new = original
        new = new.replace(".", ",")  # . would be interpreted as a file extension
        if new[-1] == ',':
            new = new[:-1]  # a final , would look weird though
        new = new.replace("/", " ")  # / would be interpreted as a subfile or folder
        new = ' '.join(new.split())  # removing extra whitespace
        if new != original:
            print("To make it safe for filepaths, the following safe title has been established"
                " based on the original:")
            print(original, "->", new)
            print("You can:")
            print("- Use it (hit return without typing anything)")
            print("- Use another title (type it then hit return)")
            choice = input("Your choice? ")
            if choice != "":
                return self._get_safe_title(original=choice)
        return new

    def _get_title_abr(self):
        """ Returns the project abbreviation, created from the title initials """
        title = self.raw_title.lower()  # to lowercase
        title = re.sub(r'[^\w^ ]', '', title)  # remove non-alpha characters
        words = title.split(" ")  # split on spaces
        words = [word.strip() for word in words if word]  # remove any additional whitespaces
        initials = [word[0] for word in words]  # get initials
        abr = "".join(initials)  # get string
        return abr

    def _get_full_title(self, safe_for_path:bool) -> str:
        """ Returns "[FANDOM] title"
        If safe_for_path, uses the safe version of the title """
        title = self.safe_title if safe_for_path else self.raw_title
        title = f'''[{self.fandom_abr}] {title}'''
        return title

    def get_generic_id(self) -> str:
        """ Returns the generic ID for the given data """
        return "-".join([self.fandom_abr, self.title_abr]).lower()
