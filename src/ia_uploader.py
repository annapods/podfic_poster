# -*- coding: utf-8 -*-
""" TODO test main? """

import re
from os.path import exists, basename
from sys import exit
from internetarchive import upload, get_item
from typing import Optional
from src.base_object import BaseObject
from src.project import Project
from src.project_metadata import placeholder_text, PlaceholderValue


class IAUploaderError(Exception):
    def __init__(self, id:str, message:str) -> None:
        self.id = id
        self.message = message
        super().__init__(message)


class IAUploader(BaseObject):
    """ Internet Archive uploading helper!
    Uses the official internetarchive API

    You can call:
    - upload_audio
    - upload_cover
    - upload_info
    - update_descrition """

    def __init__(self, verbose:bool=True) -> None:
        super().__init__(verbose)
    
    def load_project(self, project:Project, ia_id:Optional[str]=None, overwrite:bool=False) -> None:
        self._project_id = project.project_id
        self._files = project.files
        self._project_metadata = project.metadata

        self._identifier = ia_id if ia_id else self._generate_identifier()
        if (not IAUploader.identifier_available(self._identifier)) and (not overwrite):
            raise IAUploaderError(self._identifier, f"IA identifier already exists: {self._identifier}")
        if not IAUploader.identifier_valid(self._identifier):
            raise IAUploaderError(self._identifier, f"IA identifier invalid: {self._identifier}")
        self._project_metadata.update_md("IA Link", f"https://archive.org/details/{self._identifier}")
        
        self._ia_metadata = {
            'collection': 'opensource_audio',
            'title': self._project_id.raw_title,
            'mediatype': 'audio',
            'creator': 'Annapods',
            'subject': 'podfic',
            'noindex': 'true'
        }


    @staticmethod
    def identifier_available(identifier):
        """ Checks/returns the availability of the given item identifier """
        item = get_item(identifier)
        return not item.exists
    
    @staticmethod
    def identifier_valid(identifier):
        """ Checks/returns the validity of the given item identifier """
        return len(identifier) > 5 \
            and len(identifier) < 101 \
            and re.sub(r'[^a-z0-9-]', '', identifier.lower()) == identifier


    def _generate_identifier(self):
        """ Generates and returns a new ia item identifier based on fandom and work title """
    
        def safe_string(string:str) -> str:
            """ Lower, delete anything not ASCII """
            return re.sub(r'[\W]', '', string.lower())
        
        title = safe_string(self._project_id.title_abr)
        fandom = safe_string(self._project_id.fandom_abr)

        # Get generic identifier
        identifier = f"{fandom}-{title}"
        while len(identifier) <= 5:
            identifier += title

        # Probably not needed, but crop to max limit
        identifier = identifier[:100]

        return  identifier


    def _upload_file(self, file_path):
        """ Uploads the given file to the ia item """
        request = upload(
            self._identifier,
            files = [file_path],
            metadata = self._ia_metadata,
            retries = 5,
            retries_sleep = 2
        )
        self._vprint(f'{request[0].status_code} - {file_path}')


    def upload_compressed_audio(self) -> None:
        """ Uploads compressed audio files (mp3) to the ia item
        Also saves the streaming links to the work info """
        self._vprint("Uploading compressed podfic files to ia...")
        for path in self._files.audio.compressed.formatted:
            self._upload_file(path)

        # Adding the mp3 links to the metadata for ao3 streaming
        links = ["https://archive.org/download/" \
            + f"{self._identifier}/{basename(path)}"
            for path in self._files.audio.compressed.formatted]
        self._project_metadata.update_md("IA Streaming Links", links)
        self._vprint("Done!\n")


    def upload_raw_audio(self) -> None:
        """ Uploads raw audio files (wav) to the ia item """
        self._vprint("Uploading raw podfic files to ia...")
        for path in self._files.audio.raw.formatted:
            self._upload_file(path)
        # TODO In case there is no wav file, but maybe a zipped audacity file or such


    def upload_cover(self):
        """ Uploads cover art files (png and svg) to the ia item
        Also saves the cover link to the work info """
        self._vprint("Uploading cover art to ia...")
        for path in self._files.cover.compressed + self._files.cover.raw:
            self._upload_file(path)
        if self._files.cover.compressed:
            link = "https://archive.org/download/" \
                + f"{self._identifier}/{basename(self._files.cover.compressed[0])}"
            self._project_metadata.update_md("IA Cover Link", link)
            self._vprint("Done!\n")
        else:
            self._vprint("No cover found.\n")


    def upload_metadata(self):
        """ Uploads the metadata file to the ia item """
        self._vprint("Uploading podfic info to ia...")
        self._upload_file(self._files.metadata)
        self._vprint("Done!\n")


    def update_description(self):
        """ Updates item description with ao3 link """
        self._vprint("Adding podfic link to ia...", end=" ")

        if placeholder_text(self._project_metadata["Podfic Link"]):
            raise PlaceholderValue("Podfic Link", self._project_metadata["Podfic Link"])

        description = '<strong>Link to podfic:</strong> ' \
            + f'<a href="{self._project_metadata["Podfic Link"]}">ao3</a>'
        item = get_item(self._identifier)
        _ = item.modify_metadata(metadata={'description': description})
        self._vprint("Done!\n")


# #  For batch edits, use search_items
# #  Example: hiding everything from search engines retroactively
# from internetarchive import search_items
# for item in search_items('uploader:annabelle.myrt@gmail.com').iter_as_items():
#     print()
#     print(item.metadata)
#     print()
#     item.modify_metadata(dict(noindex='true'))
#     print(item.metadata)
#     print()
#     print("---------------------")
