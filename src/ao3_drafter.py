# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" Copied/adapted from https://ao3-poster.readthedocs.io/en/latest/index.html """

from json import load as js_load, dump as js_dump
from re import compile as re_compile
from bs4 import SoupStrainer, BeautifulSoup
from requests import Response, Session
from typing import Optional, List, Tuple, Dict
from src.template_filler import Ao3Template
from src.base_object import BaseObject, DebugError
from src.project_metadata import not_placeholder_link, not_placeholder_text
from src.project import Project


AO3_URL = 'https://archiveofourown.org/'
LOGIN_URL = AO3_URL+'users/login'


class Ao3DrafterError(Exception): pass


class Ao3Poster(BaseObject):
    """ Ao3 posting helper!
    Uses ao3-poster to create an ao3 draft
     """

    def __init__(self, project:Project, recompute:bool=False, verbose:bool=True) -> None:
        super().__init__(verbose)
        self._project_id = project.project_id
        self._files = project.files
        self._metadata = project.metadata
        self._template = Ao3Template(project, recompute, verbose)
        self._get_session()
        self._get_new_work_codes_and_auth_token()

    @staticmethod
    def _validate_response_url(response:Response) -> None:
        """ Raises exceptions if the response indicates a lost session or some other problem """
        url = response.headers['Location'] if response.status_code == 302 else response.url
        if url == LOGIN_URL: raise Ao3DrafterError("Ao3 login required")
        if url == AO3_URL+"auth_error": raise Ao3DrafterError("Ao3 session expired")
        if url == AO3_URL+"lost_cookie": raise Ao3DrafterError("Lost ao3 cookie, session expired")

    @staticmethod
    def _get_authenticity_token(text:str, form_id:str) -> str:
        """ Extracts the authenticity token from the page """
        strainer = SoupStrainer(id=form_id)
        soup = BeautifulSoup(text, 'lxml', parse_only=strainer)
        return soup.find(attrs={'name': 'authenticity_token'})['value']

    @staticmethod
    def _get_languages(text:str) -> Dict[str,str]:
        """ Extracts language options and the corresponding codes from given page """
        strainer = SoupStrainer(id='work_language_id')
        soup = BeautifulSoup(text, 'lxml', parse_only=strainer)
        options = soup.find_all('option')
        return {option.string: option['value'] for option in options if option['value']}

    @staticmethod
    def _get_own_pseuds(text):
        """ Extracts own pseud options and the corresponding codes from given page """
        strainer = SoupStrainer(id='work_author_attributes_ids')
        soup = BeautifulSoup(text, 'lxml', parse_only=strainer)
        # If several pseuds
        options = soup.find_all('option')
        if options:
            return {option.string: option['value']for option in options}
        # If only one pseud
        user_id = soup.find(id='work_author_attributes_ids')['value']
        regex = re_compile(r'^/users/([^/]+)$')
        strainer = SoupStrainer('a', href=regex)
        soup = BeautifulSoup(text, 'lxml', parse_only=strainer)
        dashboard_href = soup.a['href']
        matches = regex.search(dashboard_href)
        pseud = matches.group(1)
        return {pseud: user_id}


    def _get_session(self) -> None:
        """ Fetches credentials and logs in to an ao3 session. """
        self._vprint("Logging in to ao3...", end=" ")
        # Ao3 credentials should be saved in the settings file
        with open("settings.json", "r") as file:
            settings = js_load(file)
            # If they are not, the first attempt at loging in will fail and the program will ask in cli
            username = settings.get("ao3_username", "")
            password = settings.get("ao3_password", "")

        session = Session()
        # AO3 blocks python-requests by default so we need to fake a different user agent
        session.headers.update({'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' +\
            'AppleWebKit/537.36 (KHTML, like Gecko) ' +\
            'Chrome/39.0.2171.95 Safari/537.36',  # noqa: E501
        })

        # Authenticity token for log in
        response = session.get(LOGIN_URL)
        authenticity_token = Ao3Poster._get_authenticity_token(response.text, 'loginform')

        # Log in
        login_data = {
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'user[login]': username,
            'user[password]': password,
            'commit': 'Log In',
        }
        response = session.post(LOGIN_URL, login_data, allow_redirects=False)

        # Check for one cause of failure: wrong credentials
        if "The password or user name you entered doesn't match our records." in response.text:
            # Use the CLI interface to ask the user for input
            settings["ao3_username"] = input("ao3 username? ")
            settings["ao3_password"] = input("ao3 password? ")
            # Save the credentials and try again
            with open("settings.json", 'w') as file: js_dump(settings, file)
            session = self._get_session()
        # Other types of failure are not checked and will probably raise an exception later on
        
        self.session = session
        self._vprint("Done!")


    def _get_new_work_codes_and_auth_token(self) -> None:
        """ Fetches the info necessary to post a new work:
        - authenticity token for new work
        - language codes
        - own pseud codes """
        # Get an authenticity token
        response = self.session.get(AO3_URL+'works/new', allow_redirects=False)
        Ao3Poster._validate_response_url(response)
        self.new_work_auth = Ao3Poster._get_authenticity_token(response.text, 'work-form')
        # Get language and own pseud codes
        self.language_codes = Ao3Poster._get_languages(response.text)
        self.own_pseud_codes = Ao3Poster._get_own_pseuds(response.text)


    def draft_podfic(self) -> None:
        """ Drafts the ao3 post!
        Assuming that we're creating one draft at a time, so we're opening and closing the
        session at each call """
        self._vprint("Drafting podfic post to ao3...", end=" ")

        # Post formatted data
        post_data = self._get_ao3_data()
        post_url = AO3_URL+'works'
        response = self.session.post(post_url, post_data, allow_redirects=False)
        # Validate response
        if response.status_code == 500:
            raise Ao3DrafterError("Received server error: " +str(response.content))
        Ao3Poster._validate_response_url(response)
        # Raise errors
        if response.url == post_url:
            errors = []
            soup = BeautifulSoup(response.content, 'lxml')
            error = soup.find(id='error')
            if error: raise Ao3DrafterError(f"Errors while posting: {errors}, {error}")
            new_work_form = soup.find('form', id='new_work')
            if new_work_form:
                invalid_pseuds = new_work_form.find('h4', text=re_compile(r'These pseuds are invalid:'))
                if invalid_pseuds:
                    raise Ao3DrafterError(f"Invalid ao3 pseuds listed as authors: {invalid_pseuds}")
            else:
                self._vprint("draft_podfic: new_work_form == False")  # raise DebugError("draft_podfic: new_work_form == False")
        else:
            self._vprint("draft_podfic: response.url != post_url")  # raise DebugError("draft_podfic: response.url != post_url")
        # Save new work link
        link = response.headers['Location'] if response.status_code == 302 else response.url
        self._metadata.update_md(category="Podfic Link", content=link)
        # Log out
        self.session.get(AO3_URL+'users/logout')

        self._vprint("done!\n")


    def _get_ao3_data(self) -> List[Tuple[str,str]]:
        """ Creates ao3 posting data list according to ao3 API format, using Ao3Template to format
        the body and summary of the post
        NOTE post_keys might change in the future due to ao3 code changes, in which case, go to the edit
        work page and look for 'name="work'. The name and value elements make up our post_data tuples """
        self._vprint('Creating ao3 template...', end=" ")
        metadata = self._metadata  # just for convenience, bc it's pretty long...
        metadata.check_and_format(posted=False)
        # Add podfic tags
        metadata.add_podfic_tags()
        # Add Ao3 template html
        metadata.update_md("Summary", self._template.summary)
        metadata.update_md("Work Text", self._template.work_text)

        # Format info into a list of tuples using the expected keys
        post_data = []

        # Singletons to str
        for md_key, post_key in [
            ('Rating', 'work[rating_string]'),
            ('Summary', 'work[summary]'),
            ('Notes at the beginning', 'work[notes]'),
            ('Notes at the end', 'work[endnotes]'),
            ('Work Text', 'work[chapter_attributes][content]'),]:
            post_data.append((post_key, metadata[md_key]))

        # Lists to str
        for md_key, post_key in [
            ('Fandoms', 'work[fandom_string]'),
            ('Categories', 'work[category_string]'),
            ('Relationships', 'work[relationship_string]'),
            ('Characters', 'work[character_string]'),
            ('Additional Tags', 'work[freeform_string]'),]:
            post_data.append((post_key, ",".join(metadata[md_key])))

        # Lists to lists, post_key ending with []
        for md_key, post_key in [
            ('Archive Warnings', 'work[archive_warning_strings][]'),
            ]:
            for tag in metadata[md_key]: post_data.append((post_key, tag))

        # Work title
        post_data.append(("work[title]", f'[{metadata["Work Type"]}] {self._project_id.raw_title}'))

        # Own pseuds
        creators = [pseud for _, pseud in metadata["Creator/Pseud(s)"]]
        invalid_creators = set(creators) - set(self.own_pseud_codes)
        if invalid_creators: raise Ao3DrafterError('The following are not your pseuds: ' +\
            ",".join(invalid_creators) + 'Please use "Add co-creators?" for non-pseud co-creators.')
        for c in creators: post_data.append(("work[author_attributes][ids][]", self.own_pseud_codes[c]))

        # Co-creator pseuds
        post_data.append(("pseud[byline]",
            ",".join([pseud for _, pseud in metadata["Add co-creators?"] if not_placeholder_text(pseud)])))

        # Language
        if metadata["Language"] not in self.language_codes:
            raise ValueError(f'Unknown language: {metadata["Language"]} not in '+\
                str([self.language_codes[l] for l in self.language_codes]))
        post_data.append(('work[language_id]', self.language_codes[metadata["Language"]]))

        # Parent works
        for i, (link, title) in enumerate(metadata["Parent Works"]):
            if not_placeholder_link(link, title):
                post_data.append((f"work[parent_work_relationships_attributes][{i}][url]", link))

        # Archive lock for RPF
        if "RPF" in metadata["Media Category"]:
            post_data.append(('work[restricted]', '1'))

        post_data += [
            ('utf8', '✓'),
            ('authenticity_token', self.new_work_auth),
            ('preview_button', 'Preview'),  # Trigger a preview
            ('work[parent_attributes][translation]', '0'),  # Without this attribute, AO3 will try to
            # set the translation column to NULL if the work is a remix of another work
        ]

        return post_data

