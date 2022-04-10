# -*- coding: utf-8 -*-
""" WARNING not finished, doesn't work, etc
TODO more secure credentials??
https://stackoverflow.com/questions/54853197/the-smtplib-server-sendmail-function-in-python-raises-unicodeencodeerror-ascii
https://www.codespeedy.com/email-automation-in-python/
TODO May 2022 google won't allow less secure apps anymore soooo
https://www.thepythoncode.com/article/use-gmail-api-in-python"""

# import json
# import smtplib
# from email.message import EmailMessage

from project_files_tracker import FileTracker
from template_filler import DWTemplate


class DWPoster:
    """ DW poster helper!
    https://www.dreamwidth.org/manage/emailpost?mode=help """

    def __init__(self, project_handler, verbose=True):
        self._verbose = verbose
        self._project = project_handler

        # with open("settings.json", 'r') as file:
        #     edit = False
        #     settings = json.load(file)
        #     for category in ["gmail_address", "gmail_password", "dreamwidth_username"]:
        #         if category not in settings:
        #             prompt = " ".join(category.split("_")) + "? "
        #             settings[category] = input(prompt)
        #             edit = True
        # if edit:
        #     with open("settings.json", 'w') as file:
        #         json.dump(settings, file)

        # self._password = settings["gmail_password"]
        # self._gmail = settings["gmail_address"]
        # self._dw = f'{settings["dreamwidth_username"]}+PIN@post.dreamwidth.org'


    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    # def _get_email_body(self, content="", security=""):
    #     """ Generates the body of the email
    #     If content isn't specified, will be extracted from saved dw template
    #     If security isn't specified, will be set to friends-only for rpf and public otherwise """

    #     if not content:
    #         with open(self._project.files.template.dw, 'r') as file:
    #             content = file.read()

    #     security = security if security \
    #         else "access" if self._work.info["Media Category"] == "RPF" \
    #         else "public"

    #     body = "post-format: html\n" \
    #         + "post-tags: podfic\n" \
    #         + "post-security: " + security \
    #         + "\n\n" \
    #         + content \
    #         + '\n\n--\n\n'

    #     return body


    # def _get_email(self, body="", title=""):
    #     """ Generates the MIMEMultipart email object """
    #     if not title:
    #         title = f"""[{self._project.fandom.upper()}] {self._project.title.raw}"""
    #     if not body:
    #         body = self._get_email_body()
    #     email = EmailMessage()
    #     email.set_content(body)
    #     email['To'] = self._dw
    #     email['From'] = self._gmail
    #     email['Subject'] = title
    #     return email


    # def post_podfic(self, email=None):
    #     """ Post to dw account using gmail """
    #     self._vprint("Posting podfic post to dw...", end=" ")
    #     if not email:
    #         email = self._get_email()
    #     server = smtplib.SMTP('smtp.gmail.com', port=587)
    #     server.starttls()
    #     server.login(self._gmail, self._password)
    #     server.send_message(self._gmail, self._dw, email.encode("utf8"))
    #     server.quit()


    def save_dw_post_text(self, mass_xpost=True):
        """ Saves all dw posting info to the template file, ready to go!
        if mass_xpost, concatenates the html to the relevant file to enable mass posting later """

        self._vprint('Creating dw template...', end=" ")
        self._project.metadata.check_and_format(posted=True)
        post = DWTemplate(self._project).post_text

        if mass_xpost:
            self._vprint(f"saving in {FileTracker.dw_mass_xpost_file}...", end=" ")
            # But first, a quick check if we haven't already added it
            # Only relevant if posting was done in several steps, with absolutely no change to
            # the relevant data in between, so not a very common case, but *shrug*
            with open(FileTracker.dw_mass_xpost_file, 'r', encoding="utf-8") as file:
                existing = file.read()
            if post not in existing:
                with open(FileTracker.dw_mass_xpost_file, 'a', encoding="utf-8") as file:
                    post += """\n\n\n<p align="center">...</p>\n\n\n"""
                    file.write(post)
        else:
            self._vprint(f"saving in {self._project.files.template.dw}...", end=" ")
            with open(self._project.files.template.dw, 'w', encoding="utf-8") as file:
                file.write(post)

        self._vprint('done!')
