# -*- coding: utf-8 -*-
""" Project info, all of it """

from typing import Optional
from os.path import exists
from jsonpickle import encode, decode
from json import load as js_load, dump as js_dump
from src.base_object import BaseObject
from src.html_downloader import HTMLDownloader
from src.project_id import ProjectID
from src.project_metadata import ProjectMetadata
from src.project_files_tracker import FileTracker


class TrackerError(Exception):
    def __init__(self, id:str, message:str) -> None:
        self.id = id
        super().__init__(message)


class Project(BaseObject):
    """ A project! """

    def __init__(self, raw_title:str, fandom_abr:str, parent_link:Optional[str]="",
        download_parent:bool=False, reset_metadata:bool=False, verbose:bool=True) -> None:
        """ Only really useful for projects, otherwise use ProjectsTracker.get_project """
        super().__init__(verbose)

        # Create project details and files
        self.project_id = ProjectID(fandom_abr, raw_title)
        self.files = FileTracker(self.project_id, self._verbose)

        if parent_link and download_parent:
            # Downloading file
            HTMLDownloader(verbose=self._verbose).download_html(parent_link, self.files.folder)
            self.files.update_file_paths()
        if self.files.fic and reset_metadata:
            # Extracting info from html
            self.metadata = ProjectMetadata(self.files, mode="from html", verbose=self._verbose)
        elif reset_metadata:
            # Creating metadata file from scratch
            # TODO might reformat those files
            self.metadata = ProjectMetadata(self.files, mode="from scratch", verbose=self._verbose)
        else:
            # Extracting info from yaml file
            self.metadata = ProjectMetadata(self.files, mode="from yaml", verbose=self._verbose)


class ProjectsTracker(BaseObject):
    """ A project tracker """

    def __init__(self, tracker_path:str, verbose:bool=True) -> None:
        super().__init__(verbose)
        self.tracker_path = tracker_path
        if not exists(tracker_path):
            self.projects = {}
        else:
            with open(tracker_path, "r") as file:
                frozen = js_load(file)
            self.projects = decode(frozen)
    
    def get_project(self, id:str) -> Project:
        """ Returns one project based on ID """
        # Double-check ID
        if not self.id_exists(id): raise TrackerError(id, f"ID {id} unknown for this tracker")
        # Load project
        project = self.projects[id]
        # Update file paths in case they changed since last time
        # TODO try/except for if the folder has been moved...?
        project.files._project_id = project.project_id
        project.files.update_file_paths()
        # Update metadata saved in tracker with project-specific metadata file info
        project.metadata._files = project.files
        project.metadata.load()
        # TODO references don't work, because it's not pointers but values, gotta rework that structure
        # Cross-reference the rest of metadata, files and project ID
        project.project_id._files = project.files
        project.metadata._project_id = project.project_id
        project.files._metadata, project.project_id._metadata = project.metadata, project.metadata
        return project
    
    def id_exists(self, id:str) -> bool:
        """ Returns whether the ID exists in the tracker """
        return id in self.projects

    def update_project(self, id:str, project:Project, overwrite:bool=True) -> None:
        """ Saves the given project to the given ID """
        if self.id_exists(id) and not overwrite: raise TrackerError(id, f"ID {id} already exists")
        self.projects[id] = project
        self.save()
    
    def save(self) -> None:
        """ Saves the tracker """
        frozen = encode(self.projects)
        with open(self.tracker_path, 'w+') as file:
            js_dump(frozen, file)
    
