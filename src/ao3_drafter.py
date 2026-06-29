# pylint: disable=too-few-public-methods
# -*- coding: utf-8 -*-
""" Copied/adapted from https://ao3-poster.readthedocs.io/en/latest/index.html
with some bits from https://github.com/wendytg/ao3_api/blob/master/AO3/session.py """

from json import load as js_load, dump as js_dump
from re import compile as re_compile
from time import sleep
from bs4 import SoupStrainer, BeautifulSoup
from requests import Response, Session
from typing import Any, Callable, Optional, List, Tuple, Dict
from src.template_filler import Ao3Template
from src.base_object import BaseObject, DebugError
from src.project_metadata import placeholder_link, placeholder_text
from src.project import Project
from cli.cli_utils import handle_error


AO3_URL = 'https://archiveofourown.gay/'
LOGIN_URL = AO3_URL+'users/login'
WORKS_URL = AO3_URL+"works"


def ao3_draft(
        project:Project, max_tries_root:int,
        cooldown:int, verbose:bool,
        handle_error:Callable[[Exception], None]=handle_error,
        recompute:bool=True) -> None:
    """ Draft ao3 post, trying several times in case of SSL handshake error """
    def evaluate_result(_:Any) -> bool: return drafted(project)

    def get_poster():
        ao3_poster = Ao3Poster(project, verbose=verbose, recompute=recompute)
        def draft(): ao3_poster.draft_podfic()
        try_again(
            draft, evaluate_result, handle_error,
            cooldown=cooldown, max_tries=max_tries_root)

    try_again(
        get_poster, evaluate_result, handle_error,
        cooldown=cooldown, max_tries=max_tries_root)
 
def return_true(_:Any) -> bool: return True

def try_again(
        function:Callable,
        evaluate_result:Callable[[Any],bool]=return_true,
        handle_error:Callable[[Exception], None]=handle_error,
        cooldown:int=60, max_tries:int=10) -> Any:
    res = None
    found = evaluate_result(res)
    for i in range(max_tries):
        if found is False:
            try:
                res = function()
                found = evaluate_result(res)
            except Exception as e:
                handle_error(e)
                sleep(cooldown)
    return res


def drafted(project:Project) -> bool:
    link = project.metadata.get("Podfic Link")
    return link != WORKS_URL and WORKS_URL in link

def validate_ao3_response(response:Response, logged_in:bool=True) -> bool:
    if response is None: return False
    if "525: SSL handshake failed" in response.text:
        raise Ao3DrafterError(f"Code {response.status_code} - SSL handshake failed...")
    if response.url == AO3_URL+"auth_error" and logged_in:
        raise Ao3DrafterError(f"Code {response.status_code} - Authentification error")
    if response.url == AO3_URL+"lost_cookie":
        raise Ao3DrafterError(f"Code {response.status_code} - " +\
            "Lost ao3 cookie, session expired")
    # if response.text == "":
    #     raise Ao3DrafterError(f"Code {response.status_code} - Failed to get Ao3 page...")
    if "The page you were looking for doesn" in response.text:
        raise Ao3DrafterError(f"Page doesn't exist...")
    if response.status_code == 500:
        raise Ao3DrafterError("Received server error: " +str(response.content))
    if "The password or user name you entered doesn't match our records." in response.text:
        raise Ao3DrafterError("Username and/or password are wrong...")
    # if form_id and form_id not in response.text:
    #     raise Ao3DrafterError(f"Form id {form_id} not in Ao3 page...")
    return True


class Ao3DrafterError(Exception): pass


class Ao3Poster(BaseObject):
    """ Ao3 posting helper!
    Uses ao3-poster to create an ao3 draft
     """

    def __init__(self, project:Project, recompute:bool=True, verbose:bool=True) -> None:
        super().__init__(verbose)
        self._project_id = project.project_id
        self._files = project.files
        self._metadata = project.metadata
        self._template = Ao3Template(project, recompute, verbose)
        self._get_session()
        self._get_new_work_codes_and_auth_token()


    def _get_authenticity_token(
            self, url:str, form_id:str,
            allow_redirects:bool=True, return_response:bool=False
            ) -> str|Tuple[str, Response]:
        """ Extracts the authenticity token from an Ao3 page """
        response = self.session.get(url, allow_redirects=allow_redirects)
        # Check response
        validate_ao3_response(response, logged_in=False)
        # Fetch token
        strainer = SoupStrainer(id=form_id)
        soup = BeautifulSoup(response.text, 'lxml', parse_only=strainer)
        found = soup.find("input", attrs={'name': 'authenticity_token'})
        if not found:
            raise Ao3DrafterError("Couldn't find authenticity token in page??")
        # Check and return token
        if found['value'] == "":
            raise Ao3DrafterError("Authenticity token not in Ao3 page")
        if return_response:
            return found['value'], response
        else:
            return found['value']



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


    def _get_session(self, max_tries:int=5, cooldown:int=30) -> None:
        """ Fetches credentials and logs in to an ao3 session. """
        self._vprint("Logging in to ao3...", end=" ")

        # Ao3 credentials should be saved in the settings file
        with open("settings.json", "r") as file:
            settings = js_load(file)
            username = settings.get("ao3_username", "")
            password = settings.get("ao3_password", "")

        self.session = Session()
        # AO3 blocks python-requests by default so we need to fake a different user agent
        self.session.headers.update({'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' +\
            'AppleWebKit/537.36 (KHTML, like Gecko) ' +\
            'Chrome/39.0.2171.95 Safari/537.36',  # noqa: E501
        })

        # Several tries for both getting the page and getting the token
        def get_login_token() -> str:
            return self._get_authenticity_token(
                LOGIN_URL, "loginform", allow_redirects=True)
        
        def evaluate_login_token(token:str) -> bool: return token is not None and token is not ""

        def log_in():
            self._vprint("Logging in...", end=" ")
            login_data = {
                'utf8': '✓',
                'authenticity_token': try_again(
                    get_login_token, evaluate_login_token, cooldown=cooldown, max_tries=max_tries),
                'user[login]': username,
                'user[password]': password,
                'user[remember_me]': 1,
                'commit': 'Log in',
            }
            res = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
            return res
        
        res = try_again(
            log_in, validate_ao3_response, cooldown=cooldown, max_tries=max_tries)
        
        self._vprint("Done!")


    def _get_new_work_codes_and_auth_token(self, max_tries:int=15, cooldown:int=30) -> None:
        """ Fetches the info necessary to post a new work:
        - authenticity token for new work
        - language codes
        - own pseud codes """
        # Get an authenticity token
        self._vprint("Getting auth token to create new works...", end=" ")
        url = AO3_URL+"works/new"
        def function(): return self._get_authenticity_token(url, "work-form", False, True)
        def evaluate_token(token:str) -> bool: return bool(token) and token != "" and token != None
        def handle_error(e:Exception): self._vprint(str(e))
        
        self.new_work_auth, ao3_response = try_again(
            function, evaluate_token, handle_error,
            cooldown=cooldown, max_tries=max_tries)

        # Get language and own pseud codes
        self.language_codes = Ao3Poster._get_languages(ao3_response.text)
        self.own_pseud_codes = Ao3Poster._get_own_pseuds(ao3_response.text)


    def draft_podfic(self) -> None:
        """ Drafts the ao3 post!
        Assuming that we're creating one draft at a time, so we're opening and closing the
        session at each call """
        self._vprint("Drafting podfic post to ao3...", end=" ")

        # Post formatted data
        post_data = self._get_ao3_data()

        def validate_draft_response(response:Response) -> bool:
            if response == None: return False
            if response.url.endswith("/preview"):
                return True
            soup = BeautifulSoup(response.content, 'lxml')
            if not response.url == WORKS_URL:
                raise Ao3DrafterError(
                    f"Got redirected to {response.url} while trying to post")
            if "error" in response.text:
                error = soup.find(id='error')
                raise Ao3DrafterError(f"Errors while posting: {error}")
            if "new_work" not in response.text:
                raise Ao3DrafterError("No new work form in page?")
            new_work_form = soup.find('form', id='new_work')
            if new_work_form:
                invalid_pseuds = new_work_form.find(
                    'h4', text=re_compile(r'These pseuds are invalid:'))
                if invalid_pseuds:
                    raise Ao3DrafterError(
                        f"Invalid ao3 pseuds listed as authors: {invalid_pseuds}")
            else:
                print("draft_podfic: new_work_form == False")
                # raise DebugError("draft_podfic: new_work_form == False")
            raise DebugError("New case for validate_draft_response! Here are the url and the text.\nUrl:"+response.url+"\nText:"+response.text)

        def evaluate_response(response:Response) -> bool:
            try:
                validate_draft_response(response)
            except Exception as e:
                self._vprint(e)
                return False
            return True

        def try_draft() -> str: return self.session.post(
                    WORKS_URL, post_data, allow_redirects=True)

        response = try_again(try_draft, evaluate_result=validate_draft_response)

        link = response.headers['Location'] if response.status_code == 302 \
                else response.url
        link = link.replace("/preview", "")

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
            ",".join([pseud for _, pseud in metadata["Add co-creators?"] if not placeholder_text(pseud)])))

        # Language
        if metadata["Language"] not in self.language_codes:
            raise ValueError(f'Unknown language: {metadata["Language"]} not in '+\
                str([self.language_codes[l] for l in self.language_codes]))
        post_data.append(('work[language_id]', self.language_codes[metadata["Language"]]))

        # Parent works
        for i, (link, title) in enumerate(metadata["Parent Works"]):
            if not placeholder_link(link, title):
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
            ('commit', "Save Draft")
        ]

        return post_data

