# -*- coding: utf-8 -*-
""" Fandom taxonomy stuff! WIP """

from sqlite3 import connect as sqlite3_connect
from pandas import DataFrame, read_csv, concat
from os.path import exists, join, dirname


class FandomTaxonomy:
    """ Fandom taxonomy: from parent work fandom tags, preferred podficcer fandom tags,
    abbreviation and fandom categories.
    The abbreviation isn't actually used in the podfic posting helper (we need it to find the
    folder, before we get to the info). """

    @staticmethod
    def _get_canonical_key(tags):
        """ Takes a list of canonical tags, turns it into one single tag
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"]

        NOTE I checked, and the only commas in all of the canonical fandom tags on ao3 (as of
        20222-05-26) are the "、" characters in Japanese titles. To double-check, open every
        category at https://archiveofourown.org/media. """
        tags.sort()
        tags = ", ".join(tags)
        return tags

    @staticmethod
    def _get_tags_from_key(canonical_key):
        """ Turns a canonical key (string of tags joined by commas) back into separate tags """
        return canonical_key.split(", ")

    def get_all_info(self, original_tags):
        """ Gets the preferred fandom tags, the main tracker tag and the fandom cateory from
        the taxonomy.
        If unknown, asks for missing info and offers to save it.

        Takes a list of canonical tags, treats it as one single tag.
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """
        assert False, "Implement in child class, please."


class FandomTaxonomySQLite(FandomTaxonomy):
    """ Fandom taxonomy: from parent work fandom tags, preferred podficcer fandom tags,
    abbreviation and fandom categories.
    The abbreviation isn't actually used in the podfic posting helper (we need it to find the
    folder, before we get to the info).

    SQLite implementation. NOTE works, but would need some adaptations:
    - better input handling when asked to pick a number, cf CSV implementation
    - many-to-many with rel tables for everything? many-to-one for each, but list blobs? etc

    TODO get rid of the f strings and make it safe against injections """

    db_path = "fandom_taxonomy.db"

    def __init__(self, db_path=db_path):
        self._connection = sqlite3_connect(db_path)
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
            FOREIGN KEY (abr) REFERENCES AbrToCategory (abr)
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
        print(f"Wait! {target_key_name} unknown for {primary_key_value}.")

        # Can be straightforward, just input
        if not options:
            should_be = input("Value, separated with ', ' if list: ")

        # Or offer potential options
        else:
            print("Please choose one of the following:")
            for i, option in enumerate(options):
                print(i, option)
            print(len(options), "(new)")
            n_option = int(input("Your choice? "))  # TODO will fail if it's not a number, cf CSV
            if n_option >= len(options):
                should_be = input("New: ")
            else:
                should_be = options[n_option]

        # Offer to save new value
        print("We can save these preferences for next time!")
        print("- No (hit return without typing anything)")
        print("- Yes (type anything then hit return)")
        if input("Your choice? ") != "":
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



class FandomTaxonomyCSV(FandomTaxonomy):
    """ Fandom taxonomy: from parent work fandom tags, preferred podficcer fandom tags,
    abbreviation and fandom categories.
    The abbreviation isn't actually used in the podfic posting helper (we need it to find the
    folder, before we get to the info).

    CSV implementation. Every item can be the blob of a comma-separated string list.
    NOTE shouldn't work that way for abbreviations, and can there be commas in canonical tags?
    """

    csv_path = join(dirname(__file__), "fandom_taxonomy.csv")
    columns = [
        "original tags",
        "preferred tags",
        "main tracking tag",
        "abbreviation",
        "categories"]

    def __init__(self):
        if exists(FandomTaxonomyCSV.csv_path):
            self._df = read_csv(FandomTaxonomyCSV.csv_path)
        else:
            self._df = DataFrame(columns=FandomTaxonomyCSV.columns)
            self._save()

    def _save(self):
        self._df.to_csv(FandomTaxonomyCSV.csv_path, index=False)

    def get_all_info(self, original_tags):
        """ Gets the preferred fandom tags, the main tracker tag and the fandom cateory from
        the taxonomy.
        If unknown, asks for missing info and offers to save it.

        Takes a list of canonical tags, treats it as one single tag.
        This allows for one-to-many, many-to-one and many-to-many cases such as:
        - ["Batman (Comics)", "Batman - All Media Types"] -> ["Batman (Comics)"]
        - ["Women's Hockey RPF"] -> ["Hockey RPF", "Women's Hockey RPF"] """

        def pick_option(to_pick, based_on, options=[]):
            """ Offers the user all given options and to add a new one. Returns their choice. """

            # print options
            print(f"\nWhich {to_pick} for {based_on}? You can:",
                "\n- Pick a number",
                "\n- Hit return for the first item in the list (if any)",
                "\n- Or type the new value directly (separated with ', ' if it's a list)")
            for i, option in enumerate(options):
                print(f"{i}) {option}")

            # get user's choice
            choice = input("Your choice? ")
            # hit return, but no list to pick from
            if not choice and not options:
                print("We're going to need a value...")
                return pick_option(to_pick, based_on, options)
            # hit return, picking first option in the list
            elif not choice:
                n_option = 0
            else:
                # input a number from the list
                try:
                    n_option = int(choice)
                    assert 0 <= n_option < len(options)
                # anything else will be interpreted as a new value
                except ValueError:
                    return choice

            return options[n_option]

        # results
        res = [FandomTaxonomy._get_canonical_key(original_tags)]
        # (known, to_pick) pairs of categories
        categories = [(FandomTaxonomyCSV.columns[i], FandomTaxonomyCSV.columns[i+1])
            for i in range(len(FandomTaxonomyCSV.columns) - 1)]
        # dataframe of candidate rows
        candidates = self._df
        
        for known, to_pick in categories:
            # filter down candidates
            candidates = candidates.loc[candidates[known]==res[-1]]
            # get value for next category
            res.append(pick_option(to_pick, res[-1], list(candidates[to_pick])))

        if candidates.empty:
            categories = FandomTaxonomyCSV.columns
            print("You chose:")
            print(*[f"\n{category} -> {content}" for category, content in zip(categories, res)])
            print("We can save these preferences for next time!")
            print("- No (hit return without typing anything)")
            print("- Yes (type anything then hit return)")
            if input("Your choice? "):
                to_concat = DataFrame({category:[res] for category, res in zip(categories, res)})
                self._df = concat([self._df, to_concat], ignore_index=True)
                self._save()

        # turn key blobs into lists
        # also, remove canoncical tags from results
        res = [FandomTaxonomy._get_tags_from_key(key) for key in res[1:]]

        # return a list instead of a dict
        return res


    def close(self):
        """ Unused, here for compatibility with SQLite version. """
