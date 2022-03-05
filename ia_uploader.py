# -*- coding: utf-8 -*-
""" TODO test main? """

import re
import os
import sys
from internetarchive import upload, get_item


class IAUploader:
    """ Internet Archive uploading helper!
    Uses the official internetarchive API
    
    You can call:
    - upload_audio
    - upload_cover
    - upload_info
    - update_descrition """

    def __init__(self, project_info, work_info, verbose=True):
        self._verbose = verbose
        self._project = project_info
        self._work = work_info
        self._set_identifier(self._generate_identifier())
        self._metadata = {
            'collection': 'opensource_audio',
            'title': self._project.title.raw,
            'mediatype': 'audio',
            'creator': 'Annapods',
            'subject': 'podfic',
        }


    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)


    @staticmethod
    def _identifier_available(identifier):
        """ Checks/returns availability of item identifier """
        item = get_item(identifier)
        return not item.exists


    def _set_identifier(self, identifier):
        """ Sets the ia item identifier while checking for availability """

        if IAUploader._identifier_available(identifier):
            self._identifier = identifier

        else:
            print(f"/!\\ an item with the same name already exists ({identifier})")
            print("you can:")
            print("- add to the existing item (hit return)")
            print("- choose a new identifier (input the chosen identifier)")
            new = input()
            if new == "":
                self._identifier = identifier
            else:
                print(f"sure you want to create a new item {new}? nothing for yes")
                choice = input()
                if choice == "":
                    self._set_identifier(new)
                else:
                    self._set_identifier(identifier)

        # Save the link to the item in the work info
        self._work.update_info("IA Link", f"https://archive.org/details/{self._identifier}")


    def _generate_identifier(self):
        """ Generates and returns an ia item identifier based on fandom and work title """
        title = self._project.title.raw
        fandom = self._project.fandom

        # Concatenate fandom and title
        identifier = f"{fandom} {title}"
        # Lower case
        identifier = identifier.lower()
        # Replace anything not ASCII by -
        identifier = re.sub(r'[\W]', '-', identifier)
        while re.findall(r'--', identifier):
            identifier = re.sub(r'--', '-', identifier)

        while len(identifier) <= 5:
            print(f"/!\\ automatically generated identifier {identifier} is too short!")
            print("you can:")
            print("- quit (hit return)")
            print("- input a new one (input it now)")
            new = input()
            if new == "":
                sys.exit()
            else:
                identifier = new

        return identifier[:100]


    def _upload_file(self, file_path):
        """ Uploads the given file to the ia item """
        request = upload(
            self._identifier,
            files = [file_path],
            metadata = self._metadata
        )
        self._vprint(f'{request[0].status_code} - {file_path}')


    def upload_audio(self):
        """ Uploads audio files (mp3 and wav) to the ia item
        Also saves the streaming links to the work info """
        self._vprint("Uploading podfic files to ia...")
        for path in self._project.files.audio.compressed.formatted + \
            self._project.files.audio.raw.formatted:
            self._upload_file(path)
        links = ["https://archive.org/download/" \
            + f"{self._identifier}/{os.path.basename(path)}"
            for path in self._project.files.audio.compressed.formatted]
        self._work.update_info("IA Streaming Links", links)
        self._vprint("done!")


    def upload_cover(self):
        """ Uploads cover art files (png and svg) to the ia item
        Also saves the cover link to the work info """
        self._vprint("Uploading cover art to ia...")
        for path in self._project.files.cover.compressed + self._project.files.cover.raw:
            self._upload_file(path)
        link = "https://archive.org/download/" \
            + f"{self._identifier}/{os.path.basename(self._project.files.cover.compressed[0])}"
        self._work.update_info("IA Cover Link", link)
        self._vprint("done!")


    def upload_info(self):
        """ Uploads the info file (ao3 csv) to the ia item """
        self._vprint("Uploading podfic info to ia...")
        self._upload_file(self._project.files.template.ao3)
        self._vprint("done!")


    def update_description(self):
        """ Updates item description with ao3 link """
        self._vprint("Adding podfic link to ia...", end=" ")

        assert "Podfic Link" in self._work.info \
            and not self._work.info["Podfic Link"].startswith("__"), "/!\ no ao3 link yet?"

        description = '<strong>Link to podfic:</strong> ' \
            + f'<a href="{self._work.info["Podfic Link"]}"></a>'
        item = get_item(self._identifier)
        _ = item.modify_metadata(metadata={'description': description})
        self._vprint("done!")
