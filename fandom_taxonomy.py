# -*- coding: utf-8 -*-
""" Fandom taxonomy stuff! WIP """

import sqlite3
from dataclasses import dataclass
from typing import List

@dataclass
class Fandom:
    tags: List[str]
    abr: str

class FandomTaxonomy:
    """ Fandom taxonomy """

    db = "fandom_taxonomy.sql"

    def __init__(self):
        self._connection = sqlite3.connect(FandomTaxonomy.db)
        self._cursor = self._connection.cursor()
        r_good_tags = """CREATE TABLE IF NOT EXISTS GoodTags (
            tags TEXT NOT NULL,
            abr TEXT NOT NULL,
            PRIMARY KEY (tags)
            );"""
        r_bad_tags = """CREATE TABLE IF NOT EXISTS BadTags (
            original TEXT PRIMARY KEY,
            preferred TEXT NOT NULL,
            PRIMARY KEY (original),
            FOREIGN KEY (preferred) REFERENCES GoodKeys(tags)
            );"""
        self._execute([r_good_tags, r_bad_tags])

    def _execute(self, requests):
        """ Executes and commits the requests to the db """
        for request in requests:
            self._cursor.execute(request)
            self._connection.commit()

    def _fetch(self, request):
        """ Fetches the  results of the request from the db """
        return self._cursor.fetchall(request)

    @staticmethod
    def _get_canonical_key(tags):
        """ Takes a list of canonical tags, turns it into one single tag
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """
        tags = tags.sort()
        tags = ", ".join(tags)
        return tags

    @staticmethod
    def _get_tags_from_key(canonical_key):
        """ Turns a canonical key (string of tags joined by commas) back into separate tags """
        return ", ".split(canonical_key)

    def get_preferred_and_abr(self, tags):
        """ Gets the preferred and abr versions of the fandom tag from the taxonomy
        If unknown, asks for them, and offers to save them to the taxonomy
        
        Takes a list of canonical tags, treats it as one single tag
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """

        tags_key = FandomTaxonomy._get_canonical_key(tags)
        edit = False

        request = f"""SELECT preferred FROM GoodTags WHERE original = {tags_key}"""
        res = self._fetch(request)
        if res: preferred = res[0]
        if not res:
            print(f"that (combination of) fandom tag(s) is unknown: {tags_key}")
            print("please input the missing data")
            preferred = input("preferred tags, separated by ', ' (just hit return if exact same): ")
            if preferred == "": preferred = tags_key
            edit = True

        request = f"""SELECT abr FROM GoodTags WHERE tags == {preferred}"""
        res = self._fetch(request)
        if res: abr = res[0]
        if not res:
            abr = input("preferred fandom abreviation, with any uppercase letters: ")
        
        if edit:
            print("we can save these preferences for next time!")
            print("- no (hit return without typing anything)")
            print("- yes (type anything then hit return)")
            choice = input()
            if choice != "":
                pass  # TODO insert if not exists...
            
        tags = FandomTaxonomy._get_tags_from_key(preferred)
        return Fandom(tags=tags, abr=abr)

    def close(self):
        self._connection.close()
