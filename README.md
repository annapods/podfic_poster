# podfic_poster
A podfic posting helper

# set up

## venv
cd to the repertory
```python
python3.7 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ao3downloader
download code at https://github.com/nianeyna/ao3downloader, place it in the folder, unzip
move ao3download.py from the main folder to ao3downloader/actions, replacing the original file
first time running it, it will ask for user name and password, and save them in settings.json
WARNING saves settings in plain text, which is not at all secure... no idea how to do it
differently though
TODO is that circumvented yet? to test

## internetarchive
```python
ia configure
```
will ask for email and password and save them in ~/.config/internetarchive/ia.ini

## gdrive
set up oauth: https://developers.google.com/workspace/guides/create-credentials#oauth-client-id
add test users: https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918 (OAuth consent screen -> Test users)

## ao3-poster
will use the ao3-downloader settings, no need to do anything


# usage

## naming conventions
ex: "I don't wanna think anymore", Hockey RPF
fandom abbreviation:    hrpf
project title:          I don't wanna think anymore
project abbreviation:   idwta
project folder:         hrpf - idwta
wip audio files:        idwta1.mp3, idwta2.mp3, idwta.wav, ...
final audio files:      \[HRPF\] I don't wanna think anymore (1).mp3, ...
cover files:            idwta.png, idwta.svg
...

## new
```python
source .venv/bin/activate
python main.py new
```
will ask for fandom abbreviation, full project title and ao3 link
link can be to a series or to a work
will dowload the html, and create a metadata yaml file from the info in it

## post
```python
source .venv/bin/activate
python main.py post
```
will ask for fandom abbreviation and full project title
will use the files in the folder and the info in the metadata file to:
- edit metadata and cover art of audio files
- upload to gdrive
- upload to ia
- draft to ao3
- add dw post text to xpost file

# class structure

## new ProjectHandler
-> init: link:str="", fandom_abr:str="", raw_title:str="", mode:str="saved"
- id: ProjectID
    -> init: fandom_abr:str="", raw_title:str=""
    - fandom_abr: str
    - raw_title: str
    - safe_title: str
    - title_abr: str
- metadata: ProjectMetadata: collections.UserDict
    -> init: project_tracker, mode="saved"
    - data: dict
    -> update: category:str, content:??
    -> add_posting_date
    -> add_podfic_tags
    -> check_and_format: posted:bool=False
- files: FileTracker
    -> init: project_id
    - folder
    - metadata
    - templates
        - ao3
        - dw
        - TODO add tracker?
    - cover
        - compressed
        - raw
    - audio
        - compressed
            - formatted
            - unformatted
        - raw
            - formatted
            - unformatted
    -> update_file_paths

-> post

## post
- AudioHandler
    -> init: project_handler
    -> add_cover_art
    -> rename_wip_audio_files
    -> update_metadata
    -> save_audio_length
- GDriveUploader
    -> init: project_handler
    -> upload_cover
    -> upload_metadata
    -> upload_audio
    -> upload_file
- IAUploader
    -> init: project_handler
    -> upload_cover
    -> upload_metadata
    -> upload_audio
    -> upload_file
    -> update_description
- Ao3Drafter
    -> init: project_handler
    -> draft_podfic
- DWPoster
    -> init: project_handler
    -> save_dw_post_text: mass_xpost=True
- Ao3Template
    -> init: project_handler
    - summary
    - work_text
- DWTemplate
    -> init: project_handler
    - post_text

## FandomTaxonomy
-> get_all_info: original_tags:List[str] -> preferred_tags, abr, category
-> close
- AbrToCategory
    - PRIMARY abr
    - category
- MainToAbr
    - PRIMARY main_tag
    - AbrToCategories abr
- PreferredToMain
    - PRIMARY preferred_tags
    - MainToAbr main_tag
- OriginalToPreferred
    - PRIMARY original_tags
    - PreferredToMain preferred_tags