# -*- coding: utf-8 -*-
"""
Project metadata (~= posting info, ex: freeform tags)
Extracted from the parent work(s) html or from a saved file, with calls to HTMLExtractor
and templates
"""

from collections import UserDict
from datetime import date
import yaml
from typing import List, Tuple
from src.html_extractor import HTMLExtractor
from src.fandom_taxonomy import FandomTaxonomyCSV as FandomTaxonomy
# from src.fandom_taxonomy import FandomTaxonomySQLite as FandomTaxonomy
from src.base_object import VerboseObject


def not_placeholder_link(link:str, text:str) -> bool:
    """ Detects actual links, as opposed to placeholders """
    return not (link.startswith("__") or text.startswith("__"))

def remove_placeholder_links(links:List[Tuple[str,str]]) -> List[Tuple[str,str]]:
    """ Removes the placeholder links """
    return [(link, name) for link, name in links if not_placeholder_link(link, name)]


class ProjectMetadata(UserDict, VerboseObject):
    """ Keeps track of all project metadata, aka, mostly ao3 metadata

    at initialisation:
    - Use "extract" mode to extract info from html files
    - ... use "saved" mode to load info from saved info file

    afterward, use:
    - update(category, content) to update the info from outside
    - TODO create templates stuff
    """

    mass_xpost_file = "../../Music/2.3 to post/dw.txt"

    default_values = {
        # filled automatically
        "Work Title": "",
        "Language": "English",
        "Work Text": "__WORK_TEXT",
        "Podfic Link": "__PODFIC_LINK",
        "Posting Date": "__POSTING_DATE",
        "Creator/Pseud(s)": [("ao3.org/users/Annapods", "Annapods")],
        "Audio Length": "__AUDIO_LENGTH",
        "IA Link": "__URL",
        "IA Streaming Links": ["__URL1", "__URL2"],
        "IA Cover Link": "__URL",
        "GDrive Link": "__URL",
        "Media Category": "__MEDIA_CATEGORY",

        # filled automatically from the parent work html
        "Parent Works": [("__URL", "__TITLE")],
        "Writers": [("__URL", "__WRITER")],
        # "Series": self._get_series(),
        "Summary": ["__SUMMARY"],
        "Wordcount": "__WORDCOUNT",
        "Language": "__LANGUAGE",
        "Archive Warnings": [
            "__Choose Not To Use Archive Warnings",
            "__Graphic Depictions Of Violence",
            "__Major Character Death",
            "__No Archive Warnings Apply",
            "__Rape/Non-Con",
            "__Underage"],
        "Rating": "Not Rated_General Audiences_Teen And Up Audiences_Mature_Explicit",
        "Categories": [
            "__F/F", "__F/M", "__Gen", "__M/M", "__Multi", "__Other"
        ],
        "Fandoms": ["__FANDOM"],
        "Relationships": ["__PAIRING"],
        "Characters": ["__CHARACTER"],
        "Additional Tags": ["__ADTL_TAG"],

        # to fill by hand
        "Notes at the beginning": "",
        "Notes at the end": "",
        "Add co-creators?": [("__URL", "__CO_CREATOR")],
        "Cover Artist(s)": [("__URL", "__ARTIST")],
        "Work Type": "podfic",
        "Occasion": "none",
        "Tracker Notes": "",
        "Tracker Notes (cont)": "",
        "Content Notes": "Nothing I can think of, but please let me know if I missed anything.",
        "BP": False,
        "Credits": [("__URL", "__CREDIT")],
        "Stickers": False
    }


    def __init__(self, files:List[str], mode:str="from yaml", verbose:bool=True):
        """ mode can be from yaml (saved metadata), from html (using HTMLExtractor,
        with default values) or from scratch (default values only) """
        VerboseObject.__init__(self, verbose)
        UserDict.__init__(self, **ProjectMetadata.default_values)
        self._verbose = verbose
        self._save_as = files.metadata
        assert mode in ["from html", "from yaml", "from scratch"], \
            "ProjectMetadata mode must be 'from html', 'from yaml' or 'from scratch'."

        if mode == "from html":
            # Extract metadata from fic html files
            extractor = HTMLExtractor(files.fic, verbose)
            self.data.update(extractor.extract_html_data())
            # Get fandom info (preferred tags, media category) from fandom taxonomy
            self._get_fandom_info()
            # Save the metadata
            self._save()
            # print(self["Categories"])

        if mode == "from yaml":
            # Load from saved file
            with open(self._save_as, 'r') as file:
                self.data.update(yaml.safe_load(file))

        if mode == "from scratch":
            # Use placeholders
            self._save()


    def _save(self):
        """ Saves the to the yaml file """
        with open(self._save_as, 'w') as file:
            yaml.safe_dump(dict(self.data), file)

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
        # TODO regex to capture three first numbers separated by ':', for cases like
        # "00:10:49 (+freetalk: 26:45)"
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
        return ""


    def _get_fandom_info(self):
        """ Get the preferred version of the fandom tags and the media category using
        FandomTaxonomy. """
        fandom_taxonomy = FandomTaxonomy()
        preferred_tags, _, _, category = fandom_taxonomy.get_all_info(self["Fandoms"])
        self.update_md("Fandoms", preferred_tags)
        self.update_md("Media Category", category)


    def check_and_format(self, posted=False):
        """ Double checks everything is ready to fill the templates """
        at_most_one_categories = ["Summary", "Rating", "IA Link", "GDrive Link",
            "Summary", "Audio Length"]
        at_least_one_categories = ["Summary", "Rating", "IA Link", "IA Streaming Links", "GDrive Link",
            "Audio Length", "Archive Warnings", "Fandoms"]
        not_default_categories = ["Audio Length", "Media Category", "IA Link",
            "GDrive Link", "IA Streaming Links"]
        if posted:
            not_default_categories.extend(["Podfic Link", "Posting Date"])

        def assert_func(func, categories):
            for category in categories:
                assert func(category), f"/!\\ check {category}"

        def at_most_one_func(category):
            if category not in self:
                return True
            if isinstance(self[category], str):
                return True
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

        for category in self["Categories"]:
            assert category in [
                "F/F", "F/M", "Gen", "M/M", "Multi", "Other"
            ], "/!\\ check Categories"
