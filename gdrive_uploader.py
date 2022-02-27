# -*- coding: utf-8 -*-
"""
https://chingjunetao.github.io/learning/manage-google-drive-with-python/
https://stackoverflow.com/questions/30585166/create-a-folder-if-not-exists-on-google-drive-and-upload-a-file-to-it-using-py
https://stackoverflow.com/questions/70993735/pydrive-generating-a-sharable-link-to-a-file-immediately-after-upload

to set up gdrive API:
- set up oauth:
https://developers.google.com/workspace/guides/create-credentials#oauth-client-id
- add test users:
https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918
"""

# from __future__ import print_function  # TODO can we delete that one?
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os.path
from audio_handler import get_audio_file_title


class GDriveUploader:
    """ GDrive upload helper!
    Gets the paths to the file paths through a file_info object, and the work info
    through work_info.
    Automatically creates the folder (if not yet existing) and saves a shareable link
    to the work info file on creation.

    - upload_audio()
    - upload_cover()
    - upload_info()
    """

    podfic_folder_path = "podfic files"

    def __init__(self, file_info, work_info, verbose=True):
        self.verbose = verbose
        self.files = file_info
        self.work = work_info

        # Connection to API
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

        # Getting shareable folder
        self.get_podfic_folder()
        self.set_up_permission()

        # Saving link to folder in work info
        self.work.update_info("GDrive Link", self.link)


    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)


    def upload_audio(self):
        """ Uploads audio files (mp3 only) to the project's gdrive folder """
        self.vprint("Uploading podfic files to gdrive...")
        for path in self.files.mp3_finals:
            self.upload_file(path)
        self.vprint("done!")

    def upload_cover(self):
        """ Uploads cover files (all png) to the project's gdrive folder """
        self.vprint("Uploading podfic cover to gdrive...")
        for path in self.files.pngs:
            self.upload_file(path)
        self.vprint("done!")

    def upload_info(self):
        """ Uploads ao3 post info (csv file) to the project's gdrive folder """
        self.vprint("Uploading podfic info to gdrive...")
        self.upload_file(self.files.ao3)
        self.vprint("done!")

    def upload_file(self, path):
        """ Uploads the given file to the project's gdrive folder
        :args path: str, path to the file """
        self.vprint(f"{path}")
        file = self.drive.CreateFile()
        file.SetContentFile(path)
        file["title"] = os.path.basename(path)
        file["parents"] = [{"id": self.folder['id']}]
        file.Upload()


    def get_child_id(self, parent_id, child_name):
        """ Gets the id of the first element with the given name and parent

        :args parent_id: id of the parent folder
        :args child_name: name of the child element
        :returns: id of first such element encountered, else None """

        # Select by parent id
        file_list = self.drive.ListFile(
            {'q': f"'{parent_id}' in parents and trashed=false"}).GetList()

        # Select by name
        for file in file_list:
            if file['title'] == child_name:
                return file['id']

        # If no such element is found, return None -> be careful to test for it
        return None


    def get_podfic_folder(self):
        """ Get (or create) the project's gdrive folder
        Naming convention: [FANDOM] Title """

        # Get the general podfic fodler
        folders = GDriveUploader.podfic_folder_path.split("/")
        parent_id = self.get_child_id("root", folders[0])
        for child_name in folders[1:]:
            parent_id = self.get_child_id(parent_id, child_name)

        # We're using the same naming conventions as for local folders, so same function
        title = get_audio_file_title(self.files, self.work)

        # drive.CreateFile does not actually upload the file, only creates the object
        # If the filder already exists, just get it
        folder_id = self.get_child_id(parent_id, title)
        if folder_id:
            self.folder = self.drive.CreateFile({'id': folder_id})
        # Else, create it
        else:
            metadata = {'title': title,
                        "parents": [{"id": parent_id}],
                        'mimeType': 'application/vnd.google-apps.folder'}
            self.folder = self.drive.CreateFile(metadata)

        # Upload it
        self.folder.Upload()


    def set_up_permission(self):
        """ Make the folder accessible by everyone as readers, get the shareable link """

        # Open up sharing permission
        _ = self.folder.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'})

        # Upload it
        self.folder.Upload()

        # Get the shareable link
        self.link = self.folder['alternateLink']
