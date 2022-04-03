# -*- coding: utf-8 -*-
"""
Posting info
Extracted from the parent work(s) html or from a saved info file, with calls to HTMLExtractor
and templates
"""

from datetime import date
import yaml
import pandas
from template_filler import Ao3Template
from template_filler import DWTemplate
from html_extractor import HTMLExtractor
from fandom_taxonomy import FandomTaxonomy


class WorkInfo:
    """ Keeps track of work info:
    - all info, in self.info, saved in the info file
        - at initialisation, use "extract" mode to extract info from html files
        - ... use "saved" mode to load info from saved info file
        - afterward, use update_info(category, content) to update the info from outside
    - ao3 template, using Ao3Template, saved in the ao3 template file, create_ao3_template
    - dw template, using DWTemplate, saved in the dw template file or mass xpost file,
        create_dw_template
    - tracker info, not yet implemented TODO, save_tracker_info """

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

        # to fill by hand
        "Notes at the beginning": "",
        "Notes at the end": "",
        "Add co-creators?": [("__URL", "__PSEUD")],
        "Cover Artist": [],
        "Work Type": "podfic",
        "Media Category": "__MEDIA_CATEGORY",
        "Occasion": "none",
        "Tracker Notes": "",
        "Tracker Notes (cont)": "",
        "Content Notes": "If I forgot or misworded anything, please let me know!",
        "BP": False,
        "Credits": [("__URL", "__TEXT")],
        "Stickers": False
    }


    def __init__(self, project_info, mode="saved", verbose=True):
        """ mode can be saved (from yaml) or extract (from html files using HTMLExtractor,
        with default values) """
        self._verbose = verbose
        self._project = project_info
        assert mode in ["saved", "extract"], \
            "/!\\ that is not a valid mode of work info creation"

        if mode == "extract":
            extractor = HTMLExtractor(self._project.files.fic, verbose)
            self.info = extractor.extract_html_data()
            self._get_preferred_fandom_tags()
            self._add_default_fields()
            self._save_info()

        if mode == "saved":
            with open(self._project.files.info, 'r') as file:
                self.info = yaml.safe_load(file)


    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    def _save_info(self):
        """ Saves the info to the yaml info file """
        with open(self._project.files.info, 'w') as file:
            yaml.safe_dump(self.info, file)

    def update_info(self, category, content):
        """ Updates one of the fields and saves the info to the file """
        assert category in self.info, "/!\\ work info category doesn't exist"
        self.info[category] = content
        self._save_info()

    def _add_default_fields(self):
        """ Adds all missing default fields to the info """
        for key, value in WorkInfo.default_values.items():
            if key not in self.info:
                self.info[key] = value

    def add_posting_date(self):
        """ Saves the current date as the posting date
        https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python """
        self.update_info("Posting Date", date.today().strftime('%d-%m-%Y'))


    ### Additional tags

    def _add_podfic_tags(self):
        """ Adds the missing podfic tags to the additional tags """
        for tag in [
                "Podfic", "Audio Format: MP3", "Audio Format: Streaming"
            ] + [self._get_audio_length_tag()]:
            if tag not in self.info["Additional Tags"]:
                self.info["Additional Tags"].append(tag)


    def _get_audio_length_tag(self):
        """ Returns the adequate audio length additional tag """

        assert self.info["Audio Length"] != WorkInfo.default_values['Audio Length']
        hours, minutes, _ = self.info["Audio Length"].split(":")
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
        return None

    def _get_preferred_fandom_tags(self):
        """ Get the preferred version of the fandom tags using FandomTaxonomy. """
        fandom_taxonomy = FandomTaxonomy()
        preferred = fandom_taxonomy.get_preferred_fandom_tags(self.info["Fandoms"])
        self.update_info("Fandoms", preferred)

### Ao3 work text and summary

    def create_ao3_template(self):
        """ Saves all ao3 posting info to the template file, ready to go! """
        self._vprint(f'Creating ao3 template...', end=" ")
        self._check_and_format_info()
        self._add_podfic_tags()

        template = Ao3Template(self.info)
        self.info["Summary"] = template.summary
        self.info["Work text"] = template.work_text
        self._save_info()

        template = {}
        template["Work Title"] = f'[{self.info["Work Type"]}] {self._project.title.raw}'

        for key in ["Fandoms", "Relationships",
            "Characters", "Additional Tags", "Archive Warnings", "Categories"]:
            template[key] = ", ".join(self.info[key])

        for key in ["Creator/Pseud(s)", "Add co-creators?"]:
            if self.info[key]:
                pseuds = [pseud for _, pseud in self.info[key] if not pseud.startswith("__")]
                template[key] = ", ".join(pseuds)

        for key in ["Summary", "Notes at the beginning", "Notes at the end", "Language",
            "Work text", "Parent Work URL", "Rating"]:
            template[key] = self.info[key]

        if isinstance(self.info["Parent Work URL"], list):
            template["Parent Work URL"] = template["Parent Work URL"][0]

        template = pandas.DataFrame([template])
        template.to_csv(self._project.files.template.ao3)
        self._vprint(f'done! Saved in {self._project.files.template.ao3}\n')


    ### DW post

    def create_dw_template(self, mass_xpost=False):
        """ Saves all dw posting info to the template file, ready to go!
        if add_to_file, concatenates the html to the relevant file to enable mass posting later """

        self._vprint(f'Creating dw template...', end=" ")
        self._check_and_format_info(posted=True)
        post = DWTemplate(self.info).post

        if mass_xpost:
            self._vprint(f"saving in {WorkInfo.mass_xpost_file}...", end=" ")
            with open(WorkInfo.mass_xpost_file, 'a') as file:
                post += """\n\n\n<p align="center">...</p>\n\n\n"""
                file.write(post)
        else:
            self._vprint(f"saving in {self._project.files.template.dw}...", end=" ")
            with open(self._project.files.template.dw, 'w') as file:
                file.write(post)

        self._vprint('done!')


    ### Tracker

    def save_tracker_info(self):
        """ TODO... """
        self._vprint('saving tracker info...', end=" ")
        pass
        self._vprint('done!')


    ### Checks and formatting

    def _check_and_format_info(self, posted=False):
        """
        Double checks everything is ready to fill the templates
        """
        at_most_one_categories = ["Summary", "Rating", "IA Link", "GDrive Link",
            "Summary", "Audio Length"]
        at_least_one_categories = ["Summary", "Rating", "Parent Work URL",
            "IA Link", "IA Streaming Links", "GDrive Link", "Audio Length", "Archive Warnings",
            "Fandoms"]
        not_default_categories = ["Audio Length", "Media Category", "IA Link", "IA Cover Link",
            "GDrive Link", "IA Streaming Links", "Credits", "Add co-creators?"]
        if posted: not_default_categories.extend(["Podfic Link", "Posting Date"])

        def assert_func(func, categories):
            for category in categories:
                assert func(category), f"/!\\ check {category}"

        def at_most_one_func(category):
            if category not in self.info: return True
            if isinstance(self.info[category], str): return True
            if isinstance(self.info[category], list) and len(self.info[category]) == 1:
                self.info[category] = self.info[category][0]
                return True
            return False

        def at_least_one_func(category):
            return category in self.info

        def not_default_func(category):
            return self.info[category] != WorkInfo.default_values[category]
        
        assert_func(at_most_one_func, at_most_one_categories)
        assert_func(at_least_one_func, at_least_one_categories)
        assert_func(not_default_func, not_default_categories)

        assert self.info["Rating"] in [
            "Not Rated", "General Audiences", "Teen And Up Audiences", "Mature", "Explicit"
        ], f"/!\\ check ratings"

        for warning in self.info["Archive Warnings"]:
            assert warning in [
                "Choose Not To Use Archive Warnings",
                "Graphic Depictions Of Violence",
                "Major Character Death",
                "No Archive Warnings Apply",
                "Rape/Non-Con",
                "Underage"
        ], "/!\\ check Archive Warnings"
    
        for category in self.info["Categories"]:
            assert category in [
                "F/F", "F/M", "Gen", "M/M", "Multi", "Other"
            ], "/!\\ check Categories"
