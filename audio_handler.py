# -*- coding: utf-8 -*-
""" Audio files: metadata, file names, etc """

from datetime import datetime
from sys import exit as sys_exit
from os.path import exists, join
from taglib import File as taglib_File
from mutagen.mp3 import MP3
from mutagen.id3 import APIC
from base_object import VerboseObject


def get_padded_track_number_string(track_number, total_tracks):
    """ Padds track number with 0 to fit the number of digits accross all tracks """
    n_track_numerals = int(total_tracks ** 0.1)
    track_string = str(track_number)
    track_string = "".join(['0' for i in range(len(track_string) - n_track_numerals)]) \
        + track_string
    return track_string


class AudioHandler(VerboseObject):
    """ Handling audio files: renaming, updating metadata """

    def __init__(self, project_id, files, metadata, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self._files = files
        self._metadata = metadata
        self._metadata_title = self._get_audio_file_title(safe_for_path=False)
        self._file_title = self._get_audio_file_title(safe_for_path=True)


    def _get_audio_file_title(self, safe_for_path:bool):
        """ Returns "[FANDOM] title"
        If safe_for_path, uses the safe version of the title """
        title = self._project_id.safe_title if safe_for_path else self._project_id.raw_title
        title = f'''[{self._project_id.fandom_abr}] {title}'''
        return title


    def _get_artist_tag(self):
        """ Returns a formatted string for the audio files' artist metadata field
        ex: "Podder1, Podder2 (w:Writer)" """

        def get_enum(persons):
            """ Aux function, to string """
            return ", ".join([pseud for url, pseud in persons if not pseud.startswith("__")])

        artists = get_enum(
            self._metadata["Creator/Pseud(s)"] \
            + self._metadata["Add co-creators?"])

        writers = get_enum(self._metadata["Writer"])
        if writers:
            artists += f" (w:{writers})"

        return artists


    def update_metadata(self, final_files=True):
        """ Adds metadata to the mp3 and wav audio files using taglib
        By default, only to the final mp3 and wav files ; to go for the wip files instead, set
        final_files to False
        Does not add the cover art

        datetime: https://www.w3schools.com/python/python_datetime.asp
        taglib: https://pypi.org/project/pytaglib/#installation-notes """

        self._vprint("Updating metadata...")

        mp3s = self._files.audio.compressed.formatted if final_files \
            else self._files.audio.compressed.unformatted
        wavs = self._files.audio.raw.formatted if final_files \
            else self._files.audio.raw.unformatted
        for files, file_type in [(mp3s, "mp3"), (wavs, "wav")]:
            if not files:
                print(f"Could not find any {file_type} files. Do you want to...")
                print("- Continue regardless (hit return without typing anything)")
                print("- Quit (type anything then hit return)")
                choice = input("Your choice? ")
                if choice != "":
                    print("Bye!")
                    sys_exit()

        artist = self._get_artist_tag()

        for file_paths in [mp3s, wavs]:
            n_tracks = len(file_paths)
            for track_number, file_path in enumerate(file_paths):
                track_number += 1
                self._vprint(file_path)
                audio = taglib_File(file_path)
                audio.tags["TITLE"] = [self._metadata_title]
                if n_tracks > 1:
                    track_number = get_padded_track_number_string(
                        track_number+1, n_tracks)
                    audio.tags["TITLE"] = [f'{self._metadata_title} ({track_number}/{n_tracks})']
                audio.tags["ALBUM"] = [self._metadata_title]
                audio.tags["ARTIST"] = [artist]
                audio.tags["TRACKNUMBER"] = [f"{track_number}/{n_tracks}"]
                audio.tags["GENRE"] = ["Podfic"]
                audio.tags["DATE"] = [str(datetime.now().year)]
                audio.save()

        self._vprint("Done!\n")

    def save_audio_length(self):
        """ Gets the total audio length and saves it in the info file
        https://stackoverflow.com/questions/538666/format-timedelta-to-string """
        seconds = sum([taglib_File(file_path).length for file_path \
            in self._files.audio.compressed.formatted])
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        def pad_time(number):
            """ Pads a number to be minimum two characters long
            ex: 5 -> 05 """
            number = str(int(number))
            return number if len(number) > 1 else '0'+number

        length = f'{pad_time(hours)}:{pad_time(minutes)}:{pad_time(seconds)}'
        self._metadata.update_md("Audio Length", length)


    def add_cover_art(self):
        """ Adds cover art to all mp3 audio files using mutagen
        (taglib is easier to use for tags, but can't do cover art ; mutagen can, but I couldn't
        figure out how to make it do wav files...)

        https://stackoverflow.com/questions/47346399/
        how-do-i-add-cover-image-to-a-mp3-file-using-mutagen-in-python """

        self._vprint("Adding cover art to mp3 files...", end=" ")
        if not self._files.cover.compressed:
            self._vprint("no png cover available.")
        else:
            with open(self._files.cover.compressed[0], 'rb') as file:
                data = file.read()

            for file_path in self._files.audio.compressed.formatted \
                + self._files.audio.compressed.unformatted:

                audio = MP3(file_path)
                if audio.tags is None:  # https://github.com/quodlibet/mutagen/issues/327
                    audio.add_tags()
                audio.tags.add(APIC(
                        encoding = 3, # 3 is for utf-8
                        mime = 'image/png', # image/jpeg or image/png
                        type = 3, # 3 is for the cover image
                        desc = u'Cover', # if it doesn’t work try in line 35 change the desc
                        # from “Cover” to “Cover (front)”
                        data = data
                ))
                audio.save()
            self._vprint("Done!\n")


    def rename_wip_audio_files(self):
        """ Renames audio files from wip to final title """
        self._vprint("Renaming wip files...", end=" ")
        new_path_start = join(self._files.folder, self._file_title)

        def rename_one(old, new):
            if not exists(new):
                self._vprint(f"{old} -> {new}")
                os.rename(old, new)
            else:
                self._vprint(f"trying to rename {old} -> {new} but {new} already exists")
            return new

        def rename_all(paths, ext):
            if len(paths) == 0:
                return []
            if len(paths) == 1:
                return [rename_one(paths[0], f'''{new_path_start}.{ext}''')]
            return [rename_one(
                paths[i],
                f'''{new_path_start} ''' \
                    + f'''({get_padded_track_number_string(i+1, len(paths))})''' \
                    + f'''.{ext}'''
                ) for i in range(len(paths))
            ]

        rename_all(self._files.audio.compressed.unformatted, "mp3")
        rename_all(self._files.audio.raw.unformatted, "wav")
        self._files.update_file_paths()
        self._vprint("Done!\n")
