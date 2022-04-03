# -*- coding: utf-8 -*-
""" WARNING not finished, doesn't work, etc
TODO more secure credentials??
https://stackoverflow.com/questions/54853197/the-smtplib-server-sendmail-function-in-python-raises-unicodeencodeerror-ascii
https://www.codespeedy.com/email-automation-in-python/
TODO May 2022 google won't allow less secure apps anymore soooo
https://www.thepythoncode.com/article/use-gmail-api-in-python"""

import json
import smtplib
from email.message import EmailMessage


class DWPoster:
    """ DW poster helper!
    https://www.dreamwidth.org/manage/emailpost?mode=help """

    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = project_info
        self._work = work_info

        with open("settings.json", 'r') as file:
            edit = False
            settings = json.load(file)
            for category in ["gmail_address", "gmail_password", "dreamwidth_username"]:
                if category not in settings:
                    prompt = " ".join(category.split("_")) + "? "
                    settings[category] = input(prompt)
                    edit = True
        if edit:
            with open("settings.json", 'w') as file:
                json.dump(settings, file)

        self._password = settings["gmail_password"]
        self._gmail = settings["gmail_address"]
        self._dw = f'{settings["dreamwidth_username"]}+PIN@post.dreamwidth.org'


    def _vprint(self, string:str, end:str="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    def _get_email_body(self, content="", security=""):
        """ Generates the body of the email
        If content isn't specified, will be extracted from saved dw template
        If security isn't specified, will be set to friends-only for rpf and public otherwise """
        
        if not content:
            with open(self._project.files.template.dw, 'r') as file:
                content = file.read()
        
        security = security if security \
            else "access" if self._work.info["Media Category"] == "RPF" \
            else "public"

        body = "post-format: html\n" \
            + "post-tags: podfic\n" \
            + "post-security: " + security \
            + "\n\n" \
            + content \
            + '\n\n--\n\n'

        return body


    def _get_email(self, body="", title=""):
        """ Generates the MIMEMultipart email object """
        if not title:
            title = f"""[{self._project.fandom.upper()}] {self._project.title.raw}"""
        if not body:
            body = self._get_email_body()
        email = EmailMessage()
        email.set_content(body)
        email['To'] = self._dw
        email['From'] = self._gmail
        email['Subject'] = title
        return email


    def post_podfic(self, email=None):
        """ Post to dw account using gmail """
        self._vprint("Posting podfic post to dw...", end=" ")
        if not email:
            email = self._get_email()
        server = smtplib.SMTP('smtp.gmail.com', port=587)
        server.starttls()
        server.login(self._gmail, self._password)
        server.send_message(self._gmail, self._dw, email.encode("utf8"))
        server.quit()
