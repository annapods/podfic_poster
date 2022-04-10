# -*- coding: utf-8 -*-
"""
Project metadata (~= posting, ex: freeform tags)
Extracted from the parent work(s) html or from a saved file, with calls to HTMLExtractor
and templates
"""

from datetime import date
import yaml
from collections import UserDict
from datetime import date
import yaml
import pandas
from template_filler import Ao3Template
from template_filler import DWTemplate
from html_extractor import HTMLExtractor
from fandom_taxonomy import FandomTaxonomy


class ProjectMetadata(UserDict):
    """ Keeps track of all project metadata, aka, mostly ao3 metadata

    at initialisation:
    - use "extract" mode to extract info from html files
    - ... use "saved" mode to load info from saved info file

    afterward, use:
    - update(category, content) to update the info from outside
    - TODO create templates stuff
    """

    mass_xpost_file = "../../../Musique/2.5 to post/dw.txt"

    default_values = {
        # filled automatically at some point
        "Language": "English",
        "Work text": "__WORK_TEXT",
        "Podfic Link": "__PODFIC_LINK",
        "Posting Date": "__POSTING_DATE",
        "Creator/Pseud(s)": [("ao3.org/users/Annapods", "Annapods")],
        "Audio Length": "__AUDIO_LENGTH",
        "IA Link": "__URL",
        "IA Streaming Links": ["__URL1", "__URL2"],
        "IA Cover Link": "__URL",
        "GDrive Link": "__URL",
        "Media Category": "__MEDIA_CATEGORY",

        # to fill by hand
        "Notes at the beginning": "",
        "Notes at the end": "",
        "Add co-creators?": [("__URL", "__PSEUD")],
        "Cover Artist": [],
        "Work Type": "podfic",
        "Occasion": "none",
        "Tracker Notes": "",
        "Tracker Notes (cont)": "",
        "Content Notes": "If I forgot or misworded anything, please let me know!",
        "BP": False,
        "Credits": [("__URL", "__TEXT")],
        "Stickers": False
    }


    def __init__(self, project_tracker, mode="saved", verbose=True):
        """ mode can be saved (from yaml) or extract (from html files using HTMLExtractor,
        with default values) """
        super().__init__(**ProjectMetadata.default_values)
        self._verbose = verbose
        self._save_as = project_tracker.files.metadata
        assert mode in ["saved", "extract"], \
            "/!\\ that is not a valid mode of work creation"

        if mode == "extract":
            # Extract metadata from fic html files
            extractor = HTMLExtractor(project_tracker.files.fic, verbose)
            self.data.update(extractor.extract_html_data())
            # Get fandom info (preferred tags, media category) from fandom taxonomy
            self._get_fandom_info()
            # Save the metadata
            self._save()
            print(self["Category"])

        if mode == "saved":
            # Load from saved file
            with open(self._save_as, 'r') as file:
                self.data.update(yaml.safe_load(file))


    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def _save(self):
        """ Saves the to the yaml file """
        with open(self._save_as, 'w') as file:
            yaml.safe_dump(self.data, file)

    def update_md(self, category, content):
        """ Updates one of the fields and saves the to the file
        NOTE update_md in order not to overwrite dict update method. """
        assert category in self, "/!\\ work category doesn't exist"
        self[category] = content
        self._save()

    def add_posting_date(self):
        """ Saves the current date as the posting date
        https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python """
        self.update_md("Posting Date", date.today().strftime('%d-%m-%Y'))


    ### Additional tags

    def add_podfic_tags(self):
        """ Adds the missing podfic tags to the additional tags """
        tags = self["Additional Tags"]
        for tag in ["Podfic", "Audio Format: MP3", "Audio Format: Streaming"] + \
            [self._get_audio_length_tag()]:
            if tag not in tags:
                tags.append(tag)
        self.update_md("Additional Tags", tags)


    def _get_audio_length_tag(self):
        """ Returns the adequate audio length additional tag """

        assert self["Audio Length"] != ProjectMetadata.default_values['Audio Length']
        hours, minutes, _ = self["Audio Length"].split(":")
        hours, minutes = int(hours), int(minutes)

        conditions = (
            (20,  0, "Podfic Length: Over 20 Hours"),
            (15,  0, "Podfic Length: 15-20 Hours"),
            (10,  0, "Podfic Length: 10-15 Hours"),
            ( 7,  0, "Podfic Length: 7-10 Hours"),
            ( 6,  0, "Podfic Length: 6-7 Hours"),
            ( 5,  0, "Podfic Length: 5-6 Hours"),
            ( 4, 30, "Podfic Length: 4.5-5 Hours"),
            ( 4,  0, "Podfic Length: 4-4.5 Hours"),
            ( 3, 30, "Podfic Length: 3.5-4 Hours"),
            ( 3,  0, "Podfic Length: 3-3.5 Hours"),
            ( 2, 30, "Podfic Length: 2.5-3 Hours"),
            ( 2,  0, "Podfic Length: 2-2.5 Hours"),
            ( 1, 30, "Podfic Length: 1.5-2 Hours"),
            ( 1,  0, "Podfic Length: 1-1.5 Hours"),
            ( 0, 45, "Podfic Length: 45-60 Minutes"),
            ( 0, 30, "Podfic Length: 30-45 Minutes"),
            ( 0, 20, "Podfic Length: 20-30 Minutes"),
            ( 0, 10, "Podfic Length: 10-20 Minutes"),
            ( 0,  0, "Podfic Length: 0-10 Minutes")
        )

        for (min_hours, min_minutes, tag) in conditions:
            if hours >= min_hours and minutes >= min_minutes:
                return tag
        assert False, "BUG"


    def _get_fandom_info(self):
        """ Get the preferred version of the fandom tags and the media category using
        FandomTaxonomy. """
        fandom_taxonomy = FandomTaxonomy()
        preferred_tags, main_tag, abr, category = fandom_taxonomy.get_all_info(self["Fandoms"])
        self.update_md("Fandoms", preferred_tags)
        self.update_md("Media Category", category)


    def check_and_format(self, posted=False):
        """ Double checks everything is ready to fill the templates """
        at_most_one_categories = ["Summary", "Rating", "IA Link", "GDrive Link",
            "Summary", "Audio Length"]
        at_least_one_categories = ["Summary", "Rating", "Parent Work URL",
            "IA Link", "IA Streaming Links", "GDrive Link", "Audio Length", "Archive Warnings",
            "Fandoms"]
        not_default_categories = ["Audio Length", "Media Category", "IA Link", "IA Cover Link",
            "GDrive Link", "IA Streaming Links", "Credits", "Add co-creators?"]
        if posted:
            not_default_categories.extend(["Podfic Link", "Posting Date"])

        def assert_func(func, categories):
            for category in categories:
                assert func(category), f"/!\\ check {category}"

        def at_most_one_func(category):
            if category not in self: return True
            if isinstance(self[category], str): return True
            if isinstance(self[category], list) and len(self[category]) == 1:
                self[category] = self[category][0]
                return True
            return False

        def at_least_one_func(category):
            return category in self

        def not_default_func(category):
            return self[category] != ProjectMetadata.default_values[category]
        
        assert_func(at_most_one_func, at_most_one_categories)
        assert_func(at_least_one_func, at_least_one_categories)
        assert_func(not_default_func, not_default_categories)

        assert self["Rating"] in [
            "Not Rated", "General Audiences", "Teen And Up Audiences", "Mature", "Explicit"
        ], "/!\\ check ratings"

        for warning in self["Archive Warnings"]:
            assert warning in [
                "Choose Not To Use Archive Warnings",
                "Graphic Depictions Of Violence",
                "Major Character Death",
                "No Archive Warnings Apply",
                "Rape/Non-Con",
                "Underage"
        ], "/!\\ check Archive Warnings"
    
        for category in self["Category"]:
            assert category in [
                "F/F", "F/M", "Gen", "M/M", "Multi", "Other"
            ], "/!\\ check Categories"
