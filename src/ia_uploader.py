# -*- coding: utf-8 -*-
""" TODO test main? """

import re
from os.path import exists, basename
from sys import exit
from internetarchive import upload, get_item
from src.base_object import VerboseObject


class IAUploader(VerboseObject):
    """ Internet Archive uploading helper!
    Uses the official internetarchive API

    You can call:
    - upload_audio
    - upload_cover
    - upload_info
    - update_descrition """

    def __init__(self, project_id, files, metadata, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self._files = files
        self._project_metadata = metadata
        self._skip_audio = False
        self._set_identifier(self._generate_identifier())
        self._ia_metadata = {
            'collection': 'opensource_audio',
            'title': self._project_id.raw_title,
            'mediatype': 'audio',
            'creator': 'Annapods',
            'subject': 'podfic',
            'noindex': 'true'
        }


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
            print(f"An item with the same name already exists ({identifier})")
            print("You can:")
            print("- Add to, or update, all files to the existing item (hit return)")
            print("- Choose a new identifier (input the chosen identifier)")
            print("- Skip the audio files but still add or update the other, lighter, files (input ->)")

            new = input("Your choice? ")
            if new == "":
                self._identifier = identifier
            elif new == "->":
                self._skip_audio = True
                self._identifier = identifier
            else:
                choice = input(f"sure you want to create a new item {new}? nothing for yes")
                if choice == "":
                    self._set_identifier(new)
                else:
                    self._set_identifier(identifier)

        # Save the link to the item in the work info
        self._project_metadata.update_md("IA Link",
            f"https://archive.org/details/{self._identifier}")


    def _generate_identifier(self):
        """ Generates and returns an ia item identifier based on fandom and work title """
        title = self._project_id.title_abr
        fandom = self._project_id.fandom_abr

        def safe_string(string:str) -> str:
            """ Lower, delete anything not ASCII """
            return re.sub(r'[\W]', '', string.lower())

        # Get identifier
        identifier = f"{safe_string(fandom)}-{safe_string(title)}"

        while len(identifier) <= 5:
            print(f"Automatically generated identifier {identifier} is too short!")
            print("You can:")
            print("- Quit (hit return)")
            print("- input a new one (input it now)")
            new = input("Your choice? ")
            if new == "":
                exit()
            else:
                identifier = new

        return identifier[:100]


    def _upload_file(self, file_path):
        """ Uploads the given file to the ia item """
        request = upload(
            self._identifier,
            files = [file_path],
            metadata = self._ia_metadata
        )
        self._vprint(f'{request[0].status_code} - {file_path}')


    def upload_audio(self):
        """ Uploads audio files (mp3 and wav) to the ia item
        Also saves the streaming links to the work info """
        self._vprint("Uploading podfic files to ia...")

        if self._skip_audio:
            self._vprint("Skipping this step!")
            return None

        # File uploads, both mp3s and wavs
        for path in self._files.audio.compressed.formatted + \
            self._files.audio.raw.formatted:
            self._upload_file(path)
        # In case there is no wav file, but maybe a zipped audacity file or such
        if not self._files.audio.raw.formatted:
            keep_going = True
            while keep_going:
                print("Could not find any wav file. Do you want to upload some other file as",
                    "the final raw audio? (You can only pick one, if more do it manually)")
                print("- No (hit return without typing anything)")
                print("- Yes (input the path to the file then hit return)")
                print("- Quit (type quit)")
                choice = input("Your choice? ")
                if choice == "quit":
                    print("Bye!")
                    exit()
                elif choice != "":
                    if exists(choice):
                        self._upload_file(choice)
                        keep_going = False

        # Adding the mp3 links to the metadata for ao3 streaming
        links = ["https://archive.org/download/" \
            + f"{self._identifier}/{basename(path)}"
            for path in self._files.audio.compressed.formatted]
        self._project_metadata.update_md("IA Streaming Links", links)
        self._vprint("Done!\n")


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

        assert "Podfic Link" in self._project_metadata \
            and not self._project_metadata["Podfic Link"].startswith("__"), \
            "/!\\ no ao3 link yet?"

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
