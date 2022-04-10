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
            """CREATE TABLE IF NOT EXISTS AbrToCategory (
            abr TEXT NOT NULL,
            category TEXT NOT NULL,
            PRIMARY KEY (abr)
            );""",
            """CREATE TABLE IF NOT EXISTS MainToAbr (
            main_tag TEXT NOT NULL,
            abr TEXT NOT NULL,
            PRIMARY KEY (main_tag)
            FOREIGN KEY (abr) REFERENCES AbrToCategories (abr)
            );""",
            """CREATE TABLE IF NOT EXISTS PreferredToMain (
            preferred_tags TEXT NOT NULL,
            main_tag TEXT NOT NULL,
            PRIMARY KEY (preferred_tags)
            FOREIGN KEY (main_tag) REFERENCES MainToAbr (main_tag)
            );""",
            """CREATE TABLE IF NOT EXISTS OriginalToPreferred (
            original_tags TEXT NOT NULL,
            preferred_tags TEXT NOT NULL,
            PRIMARY KEY (original_tags),
            FOREIGN KEY (preferred_tags) REFERENCES PreferredToMain(preferred_tags)
            );"""
        ]
        self._execute(requests)

    def _execute(self, requests):
        """ Executes and commits the requests to the db """
        for request in requests:
            request = request.replace("'", "''")
            try:
                self._cursor.execute(request)
                self._connection.commit()
            except Exception as exception:
                print(request)
                raise exception

    def _fetch(self, request):
        """ Fetches the  results of the request from the db """
        request = request.replace("'", "''")
        try:
            self._cursor.execute(request)
        except Exception as exception:
            print(request)
            raise exception
        return self._cursor.fetchall()

    @staticmethod
    def _get_canonical_key(tags):
        """ Takes a list of canonical tags, turns it into one single tag
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """
        tags.sort()
        tags = ", ".join(tags)
        return tags

    @staticmethod
    def _get_tags_from_key(canonical_key):
        """ Turns a canonical key (string of tags joined by commas) back into separate tags """
        return canonical_key.split(", ")

    def _get_info(self, table_name, primary_key_name, primary_key_value, target_key_name,
        options=[]):
        """ Returns target_key_name values in table_name where primary_key_name is
        primary_key_value.
        If info missing, asks for it with no hinting, then offers to save it. """

        # Looking into the database...
        request = f'SELECT {target_key_name} FROM {table_name} ' + \
            f'WHERE {primary_key_name} = "{primary_key_value}"'
        res = self._fetch(request)

        # If we find a match, awesome!
        if res:
            result = res[0][0]
            return result

        # Else, we ask for the value
        print(f"{target_key_name} unknown for {primary_key_value}")

        # Can be straightforward, just input
        if not options:
            should_be = input("value, separated with ', ' if list: ")

        # Or offer potential options
        else:
            print("please choose one of the following:")
            for i, option in enumerate(options):
                print(i, option)
            print(len(options), "(new)")
            n_option = int(input("option number: "))
            if n_option >= len(options):
                should_be = input("new: ")
            else:
                should_be = options[n_option]

        # Offer to save new value
        print("we can save these preferences for next time!")
        print("- no (hit return without typing anything)")
        print("- yes (type anything then hit return)")
        if input() != "":
            requests = [
                f"""INSERT OR IGNORE INTO {table_name} ({primary_key_name}, {target_key_name})
                VALUES("{primary_key_value}", "{should_be}")"""
            ]
            self._execute(requests)

        # In any case, we return the given value
        return should_be


    def get_all_info(self, original_tags):
        """ Gets the preferred fandom tags, the main tracker tag and the fandom cateory from
        the taxonomy.
        If unknown, asks for missing info and offers to save it.

        Takes a list of canonical tags, treats it as one single tag.
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """

        original_key = FandomTaxonomy._get_canonical_key(original_tags)

        preferred_key = self._get_info(
            table_name = "OriginalToPreferred",
            primary_key_name = "original_tags",
            primary_key_value = original_key,
            target_key_name = "Preferred_tags"
        )
        main_tag = self._get_info(
            table_name = "PreferredToMain",
            primary_key_name = "preferred_tags",
            primary_key_value = preferred_key,
            target_key_name = "main_tag"
        )
        abr = self._get_info(
            table_name = "MainToAbr",
            primary_key_name = "main_tag",
            primary_key_value = main_tag,
            target_key_name = "abr"
        )

        option = self._fetch("""SELECT category FROM AbrToCategory""")
        category = self._get_info(
            table_name = "AbrToCategory",
            primary_key_name = "abr",
            primary_key_value = abr,
            target_key_name = "category",
            options=option
        )

        preferred_tags = FandomTaxonomy._get_tags_from_key(preferred_key)
        return preferred_tags, main_tag, abr, category


    def close(self):
        """ Closes the connection to the database. """
        self._connection.close()
