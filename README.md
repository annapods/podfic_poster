# podfic_poster
A podfic posting helper

# set up

## venv
cd to the repertory
python3 -m venv .venv
(or 3.7, depending)
source .venv/bin/activate
pip install -r requirements.txt

## ao3downloader
download code at https://github.com/nianeyna/ao3downloader, place it in the folder, unzip
move ao3download.py from the main folder to ao3downloader/actions, replacing the original file
first time running it, it will ask for user name and password, and save them in settings.json
WARNING saves settings in plain text, which is not at all secure... no idea how to do it
differently though

## internetarchive
ia configure
will ask for email and password and save them in ~/.config/internetarchive/ia.ini

## gdrive
set up oauth: https://developers.google.com/workspace/guides/create-credentials#oauth-client-id
add test users: https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918

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
cover files:            idwta.cover.compressed, idwta.cover.raw
...

## new
source .venv/bin/activate
python main.py new
will ask for fandom abbreviation, project abbreviation and ao3 link
link can be to a series or to a work

## post
source .venv/bin/activate
python main.py post
