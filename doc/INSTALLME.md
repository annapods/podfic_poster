
# Set up

## OS and programs

Requires python, pip and gettext. On Linux, these can be installed with:

```bash
sudo apt-get python3
sudo apt-get pip
sudo apt-get gettext
```

The latest version was tested with python3.10 on Ubuntu, but 3.7 should be fine too.

## Git

The easiest way to get the files is to clone the git repository.

To install git:

```bash
sudo apt-get git
```

To clone the repository, create a folder wherever you want, open a terminal in the folder/navigate to it, and type:

```bash
git clone https://github.com/annapods/podfic_poster.git
```

Feel free to create a branch if you want, or whatever else.

### Save modifications

```shell
git status
git add [insert files here]
git commit -m ["name of commit"] -m ["description"]
git push
git pull
```

## Path to projects

In src/project_files_tracker.py, edit the path to the parent folder of all the project folders.
In cli files, edit the path to the tracker.
TODO put that somewhere else somehow

## Virtual environment

Open up a terminal, cd to the repertory.

Linux/Mac:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows:
```bash
python3.10 -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Ao3 downloader

Code [here](https://github.com/ericfinn/ao3downloader), this is an older version of [nianeyna's project](https://github.com/nianeyna/ao3downloader) that should be compatible with python<3.9. I haven't tested it yet, though.

First time running it, it will ask for user name and password, and save them in settings.json.

WARNING saves settings in plain text, which is not very secure... no idea how to do it
differently though.

## Internet archive

```bash
ia configure
```

Will ask for email and password and save them in ~/.config/internetarchive/ia.ini.

If this step fails with an interpreter error, check that the path to the current directory doesn't contain any whitespace.

## Google drive

- [Set up oauth](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id), with URI `http://localhost:8080`
- [Add the email address attached to the gdrive account as test user](https://console.developers.google.com/apis/credentials/consent?referrer=search&project=delta-entry-341918) (OAuth consent screen -> Test users)

## Ao3 poster

Will use the ao3-downloader settings, no need to do anything.

## Template filler

In order for the template filler to work, it needs some help translating from placeholders to an actual language. Currently, only English and French are suported. To compile the necessary files:

```bash
DIR=.locales
DOMAIN=template_filler
LANG=fr
msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po
LANG=en
msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po
```

See the TRANSLATEME.txt file for information on how to add new languages. To adapt the template itself, you'll most likely need to edit the template_filler.py file and then go through the translation process again.

## Tweeter promo

[Create an app](https://developer.twitter.com/en/portal/dashboard).

- App permission: Read and write and Direct message
- Type of App: Web App, Automated App or Bot
- Callback URI / Redirect URL: https://localhost/
- Website URL: https://twitter.com/

Save the API key and secret in settings.json as twitter_api_key and twitter_api_secret, or justs run the promo program and wait for it to ask you that information.

## Tumblr promo

[Register an app](https://api.tumblr.com/console/calls/user/info):

- Application name: Podfic Promo
- Application Description: Automatically post cover art, description of podfic and link to ao3
- Application Website: https://localhost/
- Default callback URL: https://localhost/
- OAuth2 redirect URLs (space separate): https://localhost/

Save OAuth Consumer Key and Consumer Secret under tumblr_consumer_key and tumblr_consumer_secret
in settings.json, add also the name of your blog under tumblr_blog_name, or just run the promo program and wait for it to ask you those informations.

## Adapting the rest

- template_filler.py: all of it, but mostly the contact info and the feedback policy
- whatever else
