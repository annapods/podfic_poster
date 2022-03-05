# -*- coding: utf-8 -*-

from internetarchive import upload, get_item
import re
import os
from random import randint


def identifier_available(identifier):
    """ Checks/returns availability of item identifier """
    item = get_item(identifier)
    return not item.exists


class IAUploader:
    """ Internet Archive uploading helper!
    Uses the official internetarchive API """

    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = file_info
        self._work = work_info
        self.set_identifier(self.generate_identifier())
        title = self.get_title()
        self.metadata = {
            'collection': 'Community Audio',
            'title': title,
            'mediatype': 'audio',
            'creator': 'Annapods',
            'subject': 'podfic',
        }


    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    def set_identifier(self, identifier):
        """ Sets the ia item identifier while checking for availability """

        # If the item identifier doesn't exist yet, keep it
        if identifier_available(identifier):
            self.identifier = identifier

        # Else, ask the user whether to create a new item or use the existing one
        else:
            print(f"/!\\ an item with the same name already exists ({identifier})")
            if not input("do you want to add to this existing item? nothing for yes"):
                self.identifier = identifier

        # If new, then ask for another identifier
            else:
                new = input("want to pick? nothing for no/generating a random one")
                if new:
                    self.set_identifier(new)

        # If randomly generated, adds a digit to the end of the previous identifier
                else:
                    digit = randint(0, 10)
                    identifier = f"{identifier[:99]}{digit}"
                    self.set_identifier(identifier)

        # Save the link to the item
        self._work.update_info("IA Link", "https://archive.org/details/<identifier>")


    def get_title(self):
        """ Returns the title without the [podfic] """
        return re.sub('[*] ', '', self._work.info["Work Title"])


    def generate_identifier(self):
        """ Generates and returns an ia item identifier based on fandom and work title """
        title = self.get_title()
        fandom = self._project.fandom

        # Concatenate fandom and title
        identifier = f"{fandom} {title}"
        # Lower case
        identifier = identifier.lower()
        # Replace anything not ASCII by -
        identifier = re.sub(r'[\W]', '-', identifier)
        while re.findall(r'--', identifier):
            identifier = re.sub(r'--', '-', identifier)

        assert len(identifier) >= 5, \
            '/!\\ internet archive identifier cannot be shorter than 5 characters'
        return identifier[:100]


    def upload_file(self, file_path):
        """ Uploads the given file to the ia item """
        request = upload(
            self.identifier,
            files = [file_path],
            metadata = self.metadata
        )
        self._vprint(f'{request[0].status_code} - {file_path}')


    def upload_audio(self):
        """ Uploads audio files (mp3 and wav) to the ia item
        Also saves the streaming links to the work info """
        self._vprint("Uploading podfic files to ia...")
        for path in self._project.files.audio.compressed.formatted + self._project.files.audio.raw.formatted:
            self.upload_file(path)
        links = ["https://archive.org/download/" \
            + f"{self.identifier}/{os.path.basename(path)}"
            for path in self._project.files.audio.compressed.formatted]
        self._work.update_info("IA Streaming Links", links)
        self._vprint("done!")


    def upload_cover(self):
        """ Uploads cover art files (png and svg) to the ia item
        Also saves the cover link to the work info """
        self._vprint("Uploading cover art to ia...")
        for path in self._project.files.cover.compressed + self._project.files.cover.raw:
            self.upload_file(path)
        link = "https://archive.org/download/" \
            + f"{self.identifier}/{os.path.basename(self._project.files.cover.compressed[0])}"
        self._work.update_info("IA Cover Link", link)
        self._vprint("done!")


    def upload_info(self):
        """ Uploads the info file (ao3 csv) to the ia item """
        self._vprint("Uploading podfic info to ia...")
        self.upload_file(self._project.files.template.ao3)
        self._vprint("done!")


    def update_description(self):
        """ Updates item description with ao3 link """
        self._vprint("Adding podfic link to ia...", end=" ")
        assert "Podfic Link" in self._work.info \
            and not self._work.info["Podfic Link"].startswith("__"), "/!\\ no ao3 link?"
        description = '<strong>Link to podfic:</strong> ' \
            + f'<a href="{self._work.info["Podfic Link"]}"></a>'
        item = get_item(self.identifier)
        _ = item.modify_metadata(metadata={'description': description})
        self._vprint("done!")
