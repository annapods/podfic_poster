# -*- coding: utf-8 -*-
"""
Posting info
Extracted from the parent work(s) html or from a saved info file, with calls to HTMLExtractor
and templates
"""

import yaml
import os
import pandas
from template_filler import Ao3Template
from template_filler import DWTemplate
from html_extractor import HTMLExtractor


class WorkInfo:
    """ All work info: ao3 work, tracker and dw
    Calls to templates """

    default_values = {
        "Language": "English",
        "Work Text": "__WORK_TEXT",
        "Podfic Link": "__PODFIC_LINK",
        "Posting Date": "__POSTING_DATE",
        "Creator/Pseud(s)": [("ao3.org/users/Annapods", "Annapods")],

        # Additional info to fill
        "Notes at the beginning": "",
        "Notes at the end": "",
        "Add co-creators?": [("__URL", "__PSEUD")],
        "Cover Artist": [],
        "Work Type": "podfic",
        "Media Category": "__MEDIA_CATEGORY",
        "Audio Length": "__AUDIO_LENGTH",
        "Occasion": "none",
        "Tracker Notes": "",
        "Tracker Notes (cont)": "",
        "Content Notes": "If I forgot or misworded anything, please let me know!",
        "IA Link": "__URL",
        "IA Streaming Links": ["__URL1", "__URL2"],
        "IA Cover Link": "__URL",
        "GDrive Link": "__URL",
        "BP": False,
        "Credits": [("__URL", "__TEXT")],
        "Stickers": False
    }


    def __init__(self, file_info, mode="saved", verbose=True):
        """ mode can be saved (from yaml) or extract (from html files using HTMLExtractor,
        with default values) """
        self.verbose = verbose
        self.files = file_info
        assert mode in ["saved", "extract"], "/!\\ that is not a valid mode of work info creation"

        if mode == "extract":
            extractor = HTMLExtractor(file_info.html_fics, verbose)
            self.info = extractor.extract_html_data()
            self.add_default_fields()

        if mode == "saved":
            with open(self.files.yaml_info, 'r') as file:
                self.info = yaml.safe_load(file)


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def save_info(self):
        """ Saves the info to the yaml info file """
        with open(self.files.yaml_info, 'w') as f:
            yaml.safe_dump(self.info, f)

    def update_info(self, category, content):
        """ Updates one of the fields and saves the info to the file """
        assert category in self.info, "/!\\ work info category doesn't exist"
        self.info[category] = content
        self.save_info()

    def add_default_fields(self):
        """ Adds all missing default fields to the info """
        for key, value in WorkInfo.default_values.items():
            if key not in self.info:
                self.info[key] = value


    ### Additional tags

    def add_podfic_tags(self):
        """ Adds the missing podfic tags to the additional tags """
        for tag in [
                "Podfic", "Audio Format: MP3", "Audio Format: Streaming"
            ] + [self.get_audio_length_tag()]:            
            if tag not in self.info["Additional Tags"]:
                self.info["Additional Tags"].append(tag)


    def get_audio_length_tag(self):
        """ Returns the adequate audio length additional tag """

        assert self.info["Audio Length"] != WorkInfo.default_values['Audio Length']
        hours, minutes, seconds = self.info["Audio Length"].split(":")
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


    ### Ao3 work text and summary

    def create_ao3_template(self):
        self.vprint(f'Creating ao3 template...', end=" ")
        self.check_and_format_info()
        self.add_podfic_tags()

        template = Ao3Template(self.info)
        self.info["Summary"] = template.summary
        self.info["Work Text"] = template.work_text
        self.save_info()

        template = {}
        template["Work Title"] = f'[{self.info["Work Type"]}] {self.files.title}'
        for key in ["Fandoms", "Relationships",
            "Characters", "Additional Tags", "Creator/Pseud(s)", "Add co-creators?",
            "Summary", "Notes at the beginning", "Notes at the end", "Language", "Work Text",
            "Parent Work URL", "Rating", "Archive Warnings", "Categories"]:
            template[key] = self.info[key]

        if isinstance(self.info["Parent Work URL"], list):
            template["Parent Work URL"] = template["Parent Work URL"][0]

        template = pandas.DataFrame([template])
        template.to_csv(self.files.ao3)
        self.vprint(f'done!Saved in {self.files.ao3}\n')


    ### DW post

    def create_dw_template(self):
        self.vprint(f'Creating dw template...', end=" ")
        self.check_and_format_info(posted=True)

        template = DWTemplate(self.info)
        with open(self.files.dw, 'w') as f:
            f.write(template.post)

        self.vprint(f'done!')


    ### Tracker

    def save_tracker_info(self):
        self.vprint(f'saving tracker info...', end=" ")
        pass  # TODO
        self.vprint(f'done!')


    ### Checks and formatting

    def check_and_format_info(self, posted=False):
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
