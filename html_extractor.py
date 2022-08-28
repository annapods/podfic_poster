# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" Extracting data from parent work html
No argparse/main
NOTE had to add the re.DOTALL flag in _get_summaries, might have to everywhere else, too
 """

import regex as re
from base_object import VerboseObject


def flatten(list_of_lists):
    """ Aux function, flattens a list of lists into a list """
    return [item for sublist in list_of_lists for item in sublist]

def remove_dup(list_of_items):
    """ Aux function, removes duplicates from list """
    return list(set(list_of_items))


class HTMLExtractor(VerboseObject):
    """ Data extraction from downloaded ao3 html files using regex
    Use extract_html_data to get the info """

    def __init__(self, html_file_paths, verbose=True):
        super().__init__(verbose)
        self._load_html(html_file_paths)


    def _load_html(self, file_paths):
        """ Loads html files into html_works attribute """

        def decode_func(html_string):
            """ Returns the ASCII decoded version of the given HTML string
            This does NOT remove normal HTML tags like <p> """
            html_codes = (
                    ("'", '&#39;'),
                    ('"', '&quot;'),
                    ('>', '&gt;'),
                    ('<', '&lt;'),
                    ('&', '&amp;'))
            for code in html_codes:
                html_string = html_string.replace(code[1], code[0])
            return html_string

        self._html_works = []
        for path in file_paths:
            with open(path, 'r') as file:
                self._html_works.append(decode_func(file.read()))


    def _get_series(self):
        """ Extracts and returns series titles """
        regex = r"""<dt>Series:<\/dt>
        <dd>Part [0-9]+ of
<a href="http:\/\/archiveofourown.org\/series\/[0-9]*">(.*?)<\/a><\/dd>"""
        series = [re.findall(regex, work) for work in self._html_works]
        series = remove_dup(flatten(series))
        return series


    def _get_authors(self):
        """ Extracts and returns authors (url, pseud) """
        # Get author credits section
        regex = r"""<div class="byline">by (.*?)</div>"""
        blobs = [re.findall(regex, work)[0] for work in self._html_works]
        # Extract all (link, pseud) pairs from credit section
        regex = r"""<a rel="author" href="(.*?)">(.*?)<\/a>"""
        authors = [re.findall(regex, blob) for blob in blobs]
        authors = remove_dup(flatten(authors))
        return authors


    def _get_titles(self):
        """ Extracts and returns fic titles """
        regex = r"<h1>(.*?)<\/h1>"
        titles = [re.search(regex, work).group()[4:-5] for work in self._html_works]
        return titles


    def _get_wordcount(self):
        """ Extracts, sums up and returns total wordcount """
        regex = r"""(?<=<dt>Stats:<\/dt>
      <dd>
        Published: [0-9-]+
        Words: |dt>Stats:<\/dt>
      <dd>
        Published: [0-9-]+
          Completed: [0-9-]+
        Words: )[0-9]+(?=
      <\/dd>)"""
        wordcounts = [int(re.findall(regex, work)[0]) for work in self._html_works]
        return sum(wordcounts)


    def _get_summaries(self):
        """ Extracts and returns summaries """
        regex = r"""<p>Summary<\/p>
      <blockquote class="userstuff"><p>(.*?)<\/p><\/blockquote>"""
        summaries = [re.findall(regex, work, re.DOTALL)[0] for work in self._html_works]
        return summaries


    def _get_tags(self, category):
        """ Extracts and returns tags for the given category """
        regex = fr"""<dt>{category}:<\/dt>
          <dd>(.*?)<\/dd>"""
        tag_soups = [soup for work in self._html_works for soup in re.findall(regex, work)]
        regex = r"""<a href="http:\/\/archiveofourown.org\/tags\/(.*?)">(.*?)<\/a>"""
        tags = [tag for soup in tag_soups for end_url, tag in re.findall(regex, soup)]
        tags = remove_dup(tags)
        return tags


    def _get_urls(self):
        """ Extracts and returns work urls """
        regex = r"""Posted originally on the <a href="http:\/\/archiveofourown.org\/">""" \
            + r"""Archive of Our Own<\/a> at <a href="(.*?)">"""
        urls = [re.findall(regex, work) for work in self._html_works]
        return  flatten(urls)
    

    def _get_language(self):
        """ Extracts and returns work language """
        regex = fr"""<dt>Language:</dt>
        <dd>(.*?)</dd>"""
        languages = [re.findall(regex, work)[0] for work in self._html_works]
        languages = remove_dup(languages)
        if len(languages) > 1:
            self._vprint("Found several languages in parent works:", ", ".join(languages))
        return languages[0]


    def extract_html_data(self):
        """ Extracts and returns all info """
        self._vprint('Extracting data from parent work(s) html file(s)...', end=" ")
        to_return = {
            "Parent Work URL": self._get_urls(),
            "Parent Work Title": self._get_titles(),
            "Writer": self._get_authors(),
            # "Series": self._get_series(),
            "Summary": self._get_summaries(),
            "Wordcount": self._get_wordcount(),
            "Language": self._get_language(),

            "Archive Warnings": self._get_tags("Archive Warning"),
            "Rating": self._get_tags("Rating"),
            "Categories": self._get_tags("Category"),
            "Fandoms": self._get_tags("Fandom"),
            "Relationships": self._get_tags("Relationship"),
            "Characters": self._get_tags("Character"),
            "Additional Tags": self._get_tags("Additional Tags")
        }

        self._vprint('Done!')
        return to_return


if __name__ == "__main__":
    # from html_extractor import HTMLExtractor
    # import re
    test_file_paths = [input("Filepath of the html file to test on:")]
    extractor = HTMLExtractor(test_file_paths)
    info = extractor.extract_html_data()
    print(info)
