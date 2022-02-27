# -*- coding: utf-8 -*-
""" Extracting data from parent work html
No argparse/main """

import re


def flatten(list_of_lists):
    """ Aux function, flattens a list of lists into a list """
    return [item for sublist in list_of_lists for item in sublist]

def remove_dup(list_of_items):
    """ Aux function, removes duplicates from list """
    return list(set(list_of_items))


class HTMLExtractor:
    """ Data extraction from downloaded ao3 html files using regex """

    def __init__(self, html_file_paths, verbose=True):
        self.verbose = verbose
        self.load_html(html_file_paths)


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def load_html(self, file_paths):
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

        self.html_works = []
        for path in file_paths:
            with open(path, 'r') as f:
                self.html_works.append(decode_func(f.read()))


    def get_series(self):
        """ Extracts and returns series titles """
        regex =  """<dt>Series:<\/dt>
        <dd>Part [0-9]+ of
<a href="http:\/\/archiveofourown.org\/series\/[0-9]*">(.*?)<\/a><\/dd>"""
        series = [re.findall(regex, work) for work in self.html_works]
        series = remove_dup(flatten(series))
        return series


    def get_authors(self):
        """ Extracts and returns authors (url, pseud) """
        regex = """<a rel="author" href="(.*?)">(.*?)<\/a>"""
        authors = [re.findall(regex, work) for work in self.html_works]
        authors = remove_dup(flatten(authors))
        return authors


    def get_titles(self):
        """ Extracts and returns fic titles """
        regex = "<h1>(.*?)<\/h1>"
        titles = [re.search(regex, work).group()[4:-5] for work in self.html_works]
        return titles


    def get_wordcount(self):
        """ Extracts, sums up and returns total wordcount """
        regex = """<dt>Stats:<\/dt>
      <dd>
        Published: [0-9-]+
        Words: (.*?)
      <\/dd>"""
        wordcounts = [int(re.findall(regex, work)[0]) for work in self.html_works]
        return sum(wordcounts)


    def get_summaries(self):
        """ Extracts and returns summaries """
        regex = """<p>Summary<\/p>
      <blockquote class="userstuff"><p>(.*?)<\/p><\/blockquote>"""
        summaries = [re.findall(regex, work)[0] for work in self.html_works]
        return summaries


    def get_tags(self, category):
        """ Extracts and returns tags for the given category """
        regex = f"""<dt>{category}:<\/dt>
          <dd>(.*?)<\/dd>"""
        tag_soups = [soup for work in self.html_works for soup in re.findall(regex, work)]
        regex = """<a href="http:\/\/archiveofourown.org\/tags\/(.*?)">(.*?)<\/a>"""
        tags = [tag for soup in tag_soups for end_url, tag in re.findall(regex, soup)]
        tags = remove_dup(tags)
        return tags


    def get_urls(self):
        """ Extracts and returns work urls """
        regex = """Posted originally on the <a href="http:\/\/archiveofourown.org\/">Archive of Our Own<\/a> at <a href="(.*?)">"""
        urls = [re.findall(regex, work) for work in self.html_works]
        return  flatten(urls)


    def extract_html_data(self):
        """ Extracts and returns all info """
        self.vprint('Extracting data from parent work(s) html file(s)...', end=" ")
        info = {
            "Parent Work URL": self.get_urls(),
            "Parent Work Title": self.get_titles(),
            "Writer": self.get_authors(),
            "Series": self.get_series(),
            "Summary": self.get_summaries(),
            "Wordcount": self.get_wordcount(),

            "Archive Warnings": self.get_tags("Archive Warning"),
            "Rating": self.get_tags("Rating"),
            "Categories": self.get_tags("Category"),
            "Fandoms": self.get_tags("Fandom"),
            "Relationships": self.get_tags("Relationship"),
            "Characters": self.get_tags("Character"),
            "Additional Tags": self.get_tags("Additional Tags")
        }

        self.vprint(f'done!')
        return info
