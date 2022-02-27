# -*- coding: utf-8 -*-
"""
Audio files: metadata, file names, etc
"""

# from work_info import WorkInfo
import datetime
import taglib
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


def get_audio_file_title(file_info, work_info, safe_for_path=True):
    """
    Returns "[FANDOM] Title"
    If save_for_path, gets rid of forbidden characters (. and /)
    """
    fandom = file_info.fandom.upper()
    title = work_info.info["Parent Work Title"][0]
    title = f'''[{fandom}] {title}'''
    if not safe_for_path: return title
    title = title.replace(".", ",")
    title = title.replace("/", " ")
    return title


class AudioHandler:
    """
    """

    def __init__(self, file_info, work_info, verbose=True):
        self.verbose = verbose
        self.files = file_info
        self.work = work_info

    def vprint(self, string, end="\n"):
        """ Print if verbose """
        if self.verbose:
            print(string, end=end)

    def get_padded_track_number_string(self, track_number, total_tracks):
        """
        Padds track number with 0 to fit the number of digits accross all tracks
        """
        n_track_numerals = int(total_tracks ** 0.1)
        track_string = str(track_number)
        track_string = "".join(['0' for i in range(len(track_string) - n_track_numerals)]) + track_string
        return track_string

    def get_artist_tag(self):
        """
        Returns a formatted string for the audio files' artist metadata field
        ex: "Podder1, Podder2 (w:Writer)"
        """
        podders = []
        if self.work.info["Creator/Pseud(s)"]: podders.extend(self.work.info["Creator/Pseud(s)"])
        if self.work.info["Add co-creators?"]: podders.extend(self.work.info["Add co-creators?"])
        writers = self.work.info["Writer"]

        def get_enum(persons):
            return ", ".join([pseud for url, pseud in persons])
        
        artist = get_enum(podders)
        if writers: artist += f" (w:{get_enum(writers)})"

        return artist

    def update_metadata(self, final_files=True):
        """
        Adds metadata to the mp3 and wav audio files using taglib
        By default, only to the final mp3 and wav files ; to go for the wip files instead, set
        final_files to False
        Does not add the cover art

        datetime: https://www.w3schools.com/python/python_datetime.asp
        taglib: https://pypi.org/project/pytaglib/#installation-notes
        """
        self.vprint("Updating metadata...")

        mp3s = self.files.mp3_final if final_files else self.files.mp3_wip
        assert mp3s, "/!\\ tried to add mp3 metadata, couldn't find any files"
        wavs = self.files.wav_final if final_files else self.files.wav_wip
        assert wavs, "/!\\ tried to add wav metadata, couldn't find any files"

        album = get_audio_file_title(self.files, self.work, safe_for_path=False)
        artist = self.get_artist_tag()

        for file_paths in [mp3s, wavs]:
            n_tracks = len(file_paths)
            for track_number, file_path in enumerate(file_paths):
                track_number += 1
                self.vprint(file_path)
                audio = taglib.File(file_path)
                audio.tags["TITLE"] = [album]
                if n_tracks > 1:
                    track_number = self.get_padded_track_number_string(track_number, n_tracks)
                    audio.tags["TITLE"] = [f'{album} ({track_number}/{n_tracks})']
                audio.tags["ALBUM"] = album
                audio.tags["ARTIST"] = artist
                audio.tags["TRACKNUMBER"] = [f"{track_number}/{n_tracks}"]
                audio.tags["GENRE"] = ["Podfic"]
                audio.tags["DATE"] = str(datetime.datetime.now().year)
                audio.save()

        self.vprint("...done!")

    def save_audio_length(self):
        """
        Gets the total audio length and saves it in the info file
        https://stackoverflow.com/questions/538666/format-timedelta-to-string
        """
        s = sum([taglib.File(file_path).length for file_path in self.files.mp3_final])
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        length = '{}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        self.work.update_info("Audio Length", length)
        self.work.save_info()

    def add_cover_art(self):
        """
        Adds cover art to all mp3 audio files using mutagen
        (taglib is easier to use for tags, but can't do cover art ; mutagen can, but I couldn't figure out how
        to make it do wav files...)
        https://stackoverflow.com/questions/47346399/how-do-i-add-cover-image-to-a-mp3-file-using-mutagen-in-python
        """
        self.vprint("Adding cover art to mp3 files...", end=" ")
        with open(self.files.png[0], 'rb') as f:
            data = f.read()

        for file_path in self.files.mp3_final + self.files.mp3_wip:
            audio = MP3(file_path, ID3=ID3)
            audio.tags.add(APIC(
                    encoding = 3, # 3 is for utf-8
                    mime = 'image/png', # image/jpeg or image/png
                    type = 3, # 3 is for the cover image
                    desc = u'Cover', # if it doesn’t work try in line 35 change the desc from “Cover” to “Cover (front)”
                    data = data
            ))
            audio.save()
        self.vprint("done!")

    def rename_wip_audio_files(self):
        """
        Renames audio files
        """
        self.vprint("Renaming wip files...")
        new_file_start = get_audio_file_title(self.files, self.work, safe_for_path=True)
        new_path_start = os.path.join(self.files.folder, new_file_start)

        def rename_one(old, new):
            assert not os.path.exists(new), f"trying to rename {old} -> {new} but {new} already exists"
            self.vprint(f"{old} -> {new}")
            os.rename(old, new)
            return new

        def rename_all(paths, ext):
            if len(paths) == 0: return []
            if len(paths) == 1: return [rename_one(paths[0], f'''{new_path_start}.{ext}''')]
            else: return [rename_one(
                paths[i],
                f'''{new_path_start} {self.get_padded_track_number_string(i, len(paths))}.{ext}'''
                ) for i in range(len(paths))
            ]

        rename_all(self.files.mp3_wip, "mp3")
        rename_all(self.files.wav_wip, "wav")
        self.files.update_file_paths()
        self.vprint("...done!")
