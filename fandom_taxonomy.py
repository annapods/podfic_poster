# -*- coding: utf-8 -*-
""" Fandom taxonomy stuff! WIP """

import sqlite3


class FandomTaxonomy:
    """ Fandom taxonomy: from parent work fandom tags, preferred podficcer fandom tags,
    abbreviation and fandom categories.
    The abbreviation isn't actually used in the podfic posting helper (we need it to find the
    folder, before we get to the info). """

    db = "fandom_taxonomy.sql"

    def __init__(self):
        self._connection = sqlite3.connect(FandomTaxonomy.db)
        self._cursor = self._connection.cursor()
        requests = [
            """CREATE TABLE IF NOT EXISTS MainTagToAbrAndCategory (
            main_tag TEXT NOT NULL,
            abr TEXT NOT NULL,
            category TEXT PRIMARY KEY,
            PRIMARY KEY (main_tag)
            FOREIGN KEY (abr) REFERENCES AbrToCategories (abr)
            );""",
            """CREATE TABLE IF NOT EXISTS PreferredToMain (
            preferred_tags TEXT NOT NULL,
            main_tag TEXT NOT NULL,
            PRIMARY KEY (preferred_tags)
            FOREIGN KEY (main_tag) REFERENCES MainTagToAbr (main_tag)
            );""",
            """CREATE TABLE IF NOT EXISTS OriginalToPreferred (
            original_tags TEXT PRIMARY KEY,
            preferred_tags TEXT NOT NULL,
            PRIMARY KEY (original_tags),
            FOREIGN KEY (preferred_tags) REFERENCES PreferredToMain(preferred_tags)
            );"""
        ]
        self._execute(requests)

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

    def _get_missing_info(self, original_key):
        """ Takes a tag key, asks for the missing info, offers to save it, returns all info. """

        print(f"please input the missing info for {original_key}")

        request = f"""SELECT preferred_tags FROM OriginalToPreferred
            WHERE original_tags = {original_key}"""
        res = self._fetch(request)
        if res:
            preferred_tags_key = res[0]
        else:
            print(f"preferred tags are unknown for {original_key}")
            preferred_tags_key = input("preferred tags, separated by ', ' "
                "(just hit return if exact same): ")
            if preferred_tags_key == "":
                preferred_tags_key = original_key

        request = f"""SELECT main_tag FROM PreferredToMain
            WHERE preferred_tags = {preferred_tags_key}"""
        res = self._fetch(request)
        if res:
            main_tag = res[0]
        else:
            print(f"main tag is unknown for {preferred_tags_key}")
            main_tag = input("main tracking fandom tag: ")

        request = f"""SELECT abr, category FROM MainTagToAbrAndCategory
            WHERE main_tag = {main_tag}"""
        res = self._fetch(request)
        if res:
            abr, category = res[0][0], res[0][1]
        else:
            print(f"abr is unknown for {main_tag}")
            abr = input("main tracking fandom tag: ")
            print(f"category is unknwon for {main_tag} ({abr})")
            request = """SELECT category FROM MainTagToAbrAndCategory"""
            res = self._fetch(request)
            print("please choose one of the following:")
            for i, category in enumerate(res):
                print(i, category)
            print(len(res), "(new category)")
            n_category = input("category number: ")
            if n_category >= len(res):
                category = input("new category: ")
            else:
                category = res[n_category]

        print("we can save these preferences for next time!")
        print("- no (hit return without typing anything)")
        print("- yes (type anything then hit return)")
        if input() != "":
            requests = [
                f"""INSERT OR IGNORE INTO OriginalToPreferred (original_tags, preferred_tags)
                VALUES({original_key}, {preferred_tags_key})""",
                f"""INSERT OR IGNORE INTO PreferredToMain (preferred_tags, main_tag)
                VALUES({preferred_tags_key}, {main_tag})""",
                f"""INSERT OR IGNORE INTO MainTagToAbrAndCategory (main_tag, abr, category)
                VALUES({main_tag}, {abr}, {category})"""
            ]
            self._execute(requests)

        return original_key, preferred_tags_key, abr, category


    def get_info(self, original_tags):
        """ Gets the preferred fandom tags and the fandom cateory from the taxonomy.
        If unknown, uses _add_fandom to ask for them and offer to same them.

        Takes a list of canonical tags, treats it as one single tag
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """

        original_key = FandomTaxonomy._get_canonical_key(original_tags)

        request = f"""SELECT tags, category FROM OriginalToTags
            JOIN TagsToAbr USING (tag)
            JOIN AbrToCategory USING (abr)
            WHERE original = {original_key}"""
        res = self._fetch(request)
        if res:
            preferred_tags_key, fandom_category = res[0][0], res[0][1]
        else:
            print(f"that (combination of) fandom tag(s) is unknown: {original_key}")
            _, preferred_tags_key, _, fandom_category = self._get_missing_info(original_key)

        tags = FandomTaxonomy._get_tags_from_key(preferred_tags_key)
        return tags, fandom_category

    def close(self):
        """ Closes the connection to the database. """
        self._connection.close()
