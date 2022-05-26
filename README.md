# Podfic poster

A podfic posting helper!

Mostly for me, but if it can be useful feel free? MIT license I guess? I'll love you forever if you help me improve it, it's a mess.

Below is how to set it up, use it, and some details on the class structure.

## Set up

### Virtual environment

Open up a terminal, cd to the repertory.

Linux/Mac:
```python
python3.7 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
```python
python3.7 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Ao3 downloader

Code at https://github.com/nianeyna/ao3downloader, but I'm using an older version that is compatible with python3.7 so...?? And actually, are there any changes to the original code or not?

First time running it, it will ask for user name and password, and save them in settings.json.

WARNING saves settings in plain text, which is not at all secure... no idea how to do it
differently though.

### Internet archive

```python
ia configure
```

Will ask for email and password and save them in ~/.config/internetarchive/ia.ini.

### Google drive

- [Set up oauth](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
- [Add yourself as test users](https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918) (OAuth consent screen -> Test users)

### Ao3 poster

Will use the ao3-downloader settings, no need to do anything.

### Adapting the rest

- project_files_tracker.py: the path to the parent folder of all the project folders
- ?? a lot


## Usage

Posting is in two (or three, or four...) steps:

[1] Automatically getting info from ao3 -> new
    - Downloading the parent work(s)
    - Extracting metadata from the html
    - Creating the yaml file with that metadata and some placeholders
[2] Adding your own info to that
    - Editing the yaml file with any missing info
    - Double-checking everything is named right so that the program will find all the files
[3] Automatically uploading and posting and drafting -> post
    - Uploading all the files to google drive and the internet archive
    - Drafting the ao3 post
    - Saving the dreamwidth html to a text file
[4] Finishing up
    - Double-checking the ao3 draft and hitting post
    - Cross-posting to dreamwidth if you want
    - Adding the work to your tracker
    - Etc


### Naming conventions

For "I don't wanna think anymore", a Hockey RPF fic, the naming conventions would look something like this:

fandom abbreviation:    HRPF
project title:          I don't wanna think anymore
project abbreviation:   idwta
project folder:         hrpf - idwta
wip audio files:        idwta1.mp3, idwta2.mp3, idwta.wav, ...
final audio files:      \[HRPF\] I don't wanna think anymore (1).mp3, ...
cover files:            idwta.png, idwta.svg
...

### New

In a terminal, navigate to the root directory of the project and type:

Linux/Mac:

```python
source .venv/bin/activate
python main.py new
```

Windows:

```python
.venv\Scripts\activate
python main.py new
```

The program will ask for fandom abbreviation, full project title and ao3 link. That link can be to a series or to a work. It will then ask for some fandom taxonomy stuff. That can be disabled by commenting out `self._get_fandom_info()` in project_metatada.py.

### Post

Terminal, blah blah, the same line changes if you're on Windows.

```python
source .venv/bin/activate
python main.py post
```

The program will ask for fandom abbreviation and full project title. It will complain if any info is missing from the yaml file.

## Class structure

### new ProjectHandler

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

### post
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

### FandomTaxonomy
- FandomTaxonomy
-> get_all_info: original_tags:List[str] -> preferred_tags, main_tag, abr, categories
-> close

- FandomTaxonomySQLite(FandomTaxonomy)
-> AbrToCategory
    - PRIMARY abr
    - category
-> MainToAbr
    - PRIMARY main_tag
    - AbrToCategories abr
-> PreferredToMain
    - PRIMARY preferred_tags
    - MainToAbr main_tag
-> OriginalToPreferred
    - PRIMARY original_tags
    - PreferredToMain preferred_tags

- FandomTaxonomyCSV(FandomTaxonomy)
-> columns: ["original tags", "preferred tags", "main tracking tag", "abbreviation", "categories"]