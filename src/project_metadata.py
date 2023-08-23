# -*- coding: utf-8 -*-
"""
Project metadata (~= posting info, ex: freeform tags)
Extracted from the parent work(s) html or from a saved file, with calls to HTMLExtractor
and templates
"""

from collections import UserDict
from datetime import date
import yaml
from regex import search as re_search
from typing import List, Tuple, Any, Callable, Dict
from src.html_extractor import HTMLExtractor
from src.fandom_taxonomy import FandomTaxonomyCSV as FandomTaxonomy
# from src.fandom_taxonomy import FandomTaxonomySQLite as FandomTaxonomy
from src.base_object import BaseObject, DebugError


class PlaceholderValue(Exception):
    def __init__(self, key:str, value:Any) -> None:
        self.key = key
        self.value = value
        self.message = f"Placeholder value found for field {key}: {value}"
        super().__init__(self.message)


def not_placeholder_link(link:str, text:str) -> bool:
    """ Detects actual links, as opposed to placeholders """
    return not_placeholder_text(link) and not_placeholder_text(text)

def remove_placeholder_links(links:List[Tuple[str,str]]) -> List[Tuple[str,str]]:
    """ Removes the placeholder links """
    return [(link, name) for link, name in links if not_placeholder_link(link, name)]

def not_placeholder_text(text:str) -> bool:
    """ Detects actual text, as opposed to placeholders """
    return not text.startswith("__")


class ProjectMetadata(UserDict, BaseObject):
    """ Keeps track of all project metadata, aka, mostly ao3 metadata

    at initialisation:
    - Use "extract" mode to extract info from html files
    - Use "saved" mode to load info from saved info file

    afterward, use:
    - update(category, content) to update the info from outside
    - TODO create templates stuff
    """

    default_values = {
        # filled automatically
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
        "Summary": "__SUMMARY",
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


    def __init__(self, files:List[str], mode:str="from yaml", verbose:bool=True) -> None:
        """ Mode can be from yaml (saved metadata), from html (using HTMLExtractor,
        with default values) or from scratch (default values only) """
        BaseObject.__init__(self, verbose)
        UserDict.__init__(self, **ProjectMetadata.default_values)
        self._verbose = verbose
        self.save_as = files.metadata
        if mode not in ["from html", "from yaml", "from scratch"]: raise ValueError(
            f"ProjectMetadata mode must be 'from html', 'from yaml' or 'from scratch', got {mode}")

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
            self.load()

        if mode == "from scratch":
            # Use placeholders
            self._save()

    def load(self) -> None:
        """ Loads the data from the yaml file """
        with open(self.save_as, 'r') as file:
            self.data.update(yaml.safe_load(file))

    def _save(self) -> None:
        """ Saves the data to the yaml file """
        with open(self.save_as, 'w') as file:
            yaml.safe_dump(dict(self.data), file)

    def update_md(self, category:str, content:Any) -> None:
        """ Updates one of the fields and saves the to the file
        NOTE update_md in order not to overwrite dict update method. """
        if category not in self: raise KeyError(
            f"{category} metadata field doesn't exist, can't set it to {content}")
        self[category] = content
        self._save()

    def add_posting_date(self) -> None:
        """ Saves the current date as the posting date
        https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python """
        self.update_md("Posting Date", date.today().strftime('%d-%m-%Y'))


    ### Additional tags

    def add_podfic_tags(self) -> None:
        """ Adds the missing podfic tags to the additional tags """
        tags = self["Additional Tags"]
        for tag in ["Podfic", "Audio Format: MP3", "Audio Format: Streaming"] + \
            [self._get_audio_length_tag()]:
            if tag not in tags:
                tags.append(tag)
        self.update_md("Additional Tags", tags)


    def _get_audio_length_tag(self) -> None:
        """ Returns the adequate audio length additional tag """

        if self["Audio Length"] == ProjectMetadata.default_values['Audio Length']:
            raise PlaceholderValue("Audio Length", self["Audio Length"])

        regex = "^(?P<hours>[0-9]+):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9]{2})"
        found = re_search(regex, self["Audio Length"])
        if not found: raise ValueError(
            "Audio Length parameter does not fit the required {hours}:{minutes}:{seconds} format: "+\
            self["Audio Length"])
        hours, minutes = int(found.group("hours")), int(found.group("minutes"))

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

        raise DebugError(f"No canonical audio length tag found for {self['Audio Length']}")


    def _get_fandom_info(self) -> None:
        """ Get the preferred version of the fandom tags and the media category using
        FandomTaxonomy
        TODO rewrite FandomTaxonomy... """
        fandom_taxonomy = FandomTaxonomy()
        preferred_tags, _, _, category = fandom_taxonomy.get_all_info(self["Fandoms"])
        self.update_md("Fandoms", preferred_tags)
        self.update_md("Media Category", category)


    def check_and_format(self, posted:bool=False) -> None:
        """ Double checks everything is ready to fill the templates """

        for category in ["Summary", "Rating", "IA Link", "GDrive Link", "Summary", "Audio Length"]:
            if category in self and not isinstance(self[category], str) and \
                isinstance(self[category], list) and len(self[category]) < 1:
                raise ValueError(f"Too many elements for {category}: {self[category]}")
        
        for category in ["Summary", "Rating", "IA Link", "IA Streaming Links", "GDrive Link",
            "Audio Length", "Archive Warnings", "Fandoms"]:
            if not category in self:
                raise ValueError(f"Not enough elements for {category}: {self[category]}")

        for category in ["Audio Length", "Media Category", "IA Link",
            "GDrive Link", "IA Streaming Links"] + ["Podfic Link", "Posting Date"] if posted else []:
            if self[category] == ProjectMetadata.default_values[category]:
                raise PlaceholderValue(category, self[category])

        domains = [
            ("Rating", ["Not Rated", "General Audiences", "Teen And Up Audiences", "Mature","Explicit"]),
            ("Archive Warnings", ["Choose Not To Use Archive Warnings", "Graphic Depictions Of Violence",
                "Major Character Death", "No Archive Warnings Apply", "Rape/Non-Con", "Underage"]),
            ("Categories", ["F/F", "F/M", "Gen", "M/M", "Multi", "Other"])]
        

        for category, domain in domains:
            if type(self[category]) == str:
                if self[category] not in domain:
                    raise ValueError(f"Unexpected value for {category}: {self[category]}\n"+\
                        f"Should be in {domain}")
            elif type(self[category]) == list:
                for item in self[category]:
                    if item not in domain:
                        raise ValueError(f"Unexpected value for {category}: {item}\n"+\
                            f"Should be in {domain}")
            else:
                raise ValueError(
                    f"Unexpected type for {category}: should be str or list, is {self[category]}")

