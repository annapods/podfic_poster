
# Set up

## Virtual environment

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

## Ao3 downloader

Code at https://github.com/nianeyna/ao3downloader, but I'm using an older version that is compatible with python3.7 so...?? And actually, are there any changes to the original code or not?

First time running it, it will ask for user name and password, and save them in settings.json.

WARNING saves settings in plain text, which is not at all secure... no idea how to do it
differently though.

## Internet archive

```python
ia configure
```

Will ask for email and password and save them in ~/.config/internetarchive/ia.ini.

## Google drive

- [Set up oauth](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
- [Add yourself as test users](https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918) (OAuth consent screen -> Test users)

## Ao3 poster

Will use the ao3-downloader settings, no need to do anything.

## Adapting the rest

- project_files_tracker.py: the path to the parent folder of all the project folders
- template_filler.py: all of it, but mostly the contact info
- ?? a lot
