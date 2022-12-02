# -*- coding: utf-8 -*-
"""
https://chingjunetao.github.io/learning/manage-google-drive-with-python/
https://stackoverflow.com/questions/30585166/create-a-folder-if-not-exists-on-google-drive-and-upload-a-file-to-it-using-py
https://stackoverflow.com/questions/70993735/pydrive-generating-a-sharable-link-to-a-file-immediately-after-upload
"""

from os.path import basename
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from base_object import VerboseObject


class GDriveUploader(VerboseObject):
    """ GDrive upload helper!
    Gets the paths to the file paths through a file_info object, and the work info
    through work_info.
    Automatically creates the folder (if not yet existing) and saves a shareable link
    to the work info file on creation.

    - upload_audio()
    - upload_cover()
    - upload_info()
    """

    # The name of the folder with all the podfic subfolders
    podfic_folder_path = "podfic files"

    def __init__(self, project_id, files, metadata, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self._files = files
        self._metadata = metadata

        # Connection to API
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self._drive = GoogleDrive(gauth)

        # Getting shareable folder
        self._get_podfic_folder()
        self._set_up_permission()

        # Saving link to folder in work info
        self._metadata.update_md("GDrive Link", self.link)


    def upload_audio(self):
        """ Uploads audio files (mp3 only) to the project's gdrive folder """
        self._vprint("Uploading podfic files to gdrive...")
        for path in self._files.audio.compressed.formatted:
            self.upload_file(path)
        self._vprint("Done!\n")

    def upload_cover(self):
        """ Uploads cover files (all png) to the project's gdrive folder """
        self._vprint("Uploading podfic cover to gdrive...")
        for path in self._files.cover.compressed:
            self.upload_file(path)
        if self._files.cover.compressed:
            self._vprint("Done!\n")
        else:
            self._vprint("No cover found.\n")

    def upload_metadata(self):
        """ Uploads metadata file (yaml) to the project's gdrive folder """
        self._vprint("Uploading podfic info to gdrive...")
        self.upload_file(self._files.metadata)
        self._vprint("Done!\n")

    def upload_file(self, path):
        """ Uploads the given file to the project's gdrive folder
        :args path: str, path to the file """
        self._vprint(f"{path}")
        file = self._drive.CreateFile()
        file.SetContentFile(path)
        file["title"] = basename(path)
        file["parents"] = [{"id": self._folder['id']}]
        file.Upload()


    def _get_child_id(self, parent_id, child_name):
        """ Gets the id of the first element with the given name and parent

        :args parent_id: id of the parent folder
        :args child_name: name of the child element
        :returns: id of first such element encountered, else None """

        # Select by parent id
        file_list = self._drive.ListFile(
            {'q': f"'{parent_id}' in parents and trashed=false"}).GetList()

        # Select by name
        for file in file_list:
            if file['title'] == child_name:
                return file['id']

        # If no such element is found, return None -> be careful to test for it
        return None


    def _get_podfic_folder(self):
        """ Get (or create) the project's gdrive folder
        Naming convention: [FANDOM] Title """

        # Get the general podfic fodler
        folders = GDriveUploader.podfic_folder_path.split("/")
        parent_id = self._get_child_id("root", folders[0])
        for child_name in folders[1:]:
            parent_id = self._get_child_id(parent_id, child_name)

        title = f'[{self._project_id.fandom_abr.upper()}] {self._project_id.safe_title}'

        # drive.CreateFile does not actually upload the file, only creates the object
        # If the filder already exists, just get it
        folder_id = self._get_child_id(parent_id, title)
        if folder_id:
            self._folder = self._drive.CreateFile({'id': folder_id})
        # Else, create it
        else:
            metadata = {'title': title,
                        "parents": [{"id": parent_id}],
                        'mimeType': 'application/vnd.google-apps.folder'}
            self._folder = self._drive.CreateFile(metadata)

        # Upload it
        self._folder.Upload()


    def _set_up_permission(self):
        """ Make the folder accessible by everyone as readers, get the shareable link """

        # Open up sharing permission
        _ = self._folder.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'})

        # Upload it
        self._folder.Upload()

        # Get the shareable link
        self.link = self._folder['alternateLink']
