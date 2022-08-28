# Podfic poster

A podfic posting helper!

## Licence

Mostly for me, but if it can be useful feel free? MIT license I guess? I'll love you forever if you help me improve it, it's a mess.

## Setup

Cf INSTALLME.md.

## Usage

### [1] Getting a project ready for posting
 
In order to use this helper, you need to follow a few naming conventions.

For I don't wanna think anymore, a Hockey RPF fic, it would look something like this:

Fandom abbreviation:    HRPF
Project title:          I don't wanna think anymore
Project abbreviation:   idwta
Project folder:         hrpf - idwta

Wip audio files:        idwta1.mp3, idwta2.mp3, idwta.wav, ...
Final audio files:      \[HRPF\] I don't wanna think anymore (1).mp3, ...
Cover files:            idwta.png, idwta.svg
...

Cover art files are optional. Any metadata added to the audio files manually might be overwritten or deleted.

### [2] Creating the info file

Here is what the program will do:
- Download the parent work(s)
- Extract metadata from the html
- Create the yaml file with that metadata and some placeholders

And here's how to do it.

#### Project identity

In a terminal, navigate to the root directory of the project and type:

Linux/Mac:

```shell
source .venv/bin/activate
python main.py new
```

Windows:

```shell
.venv\Scripts\activate
python main.py new
```

The program will ask for fandom abbreviation and Full project title. Stick to the spelling, case, etc used in the final mp3 files. For ex, `[DCU] Wayne Enterprises.mp3` will correspond to `DCU` and `Wayne Enterprises`. 

```
Fandom abr: DCU
Full project title: Wayne Enterprises
```

The program will try to find the project folder and ask for confirmation.

```
Found a project folder! ../../../Musique/2.5 to post/dcu - we
You can:
- Use it (hit return without typing anything)
- Quit (type quit and then hit return)
- Use another folder (type the path to the folder then hit return)
Your choice?
```

#### Parent work download

It will then ask for the link to the work in order to download it and extract some metadata. The metadata will be saved in a yaml file and will need to be edited before posting.

```
Link to parent work(s): https://archiveofourown.org/works/31056044
Downloading html...
logging in
Done!
Extracting data from parent work(s) html file(s)... Done!
```

#### Fandom taxonomy

After that, the program ask for some fandom taxonomy stuff. For reference, preferred tags are the tags you want on the ao3 work. Main tracking tag is the name of the fandom in the tracker spreadsheet*. The abbreviation is used in the name and metadata of the audio files, and is the same as asked previously. Categories are the fandom categories in the tracker spreadsheet*.

*The tracker spreadsheet part isn't coded out yet. To disable the whole thing, comment out `self._get_fandom_info()` in project_metatada.py.

```
Which preferred tags for Batman - All Media Types? You can: 
- Pick a number 
- Hit return for the first item in the list (if any) 
- Or type the new value directly (separated with ', ' if it's a list)
Your choice? DCU (Comics), Batman - All Media Types

Which main tracking tag for DCU? You can: 
- Pick a number 
- Hit return for the first item in the list (if any) 
- Or type the new value directly (separated with ', ' if it's a list)
Your choice? DCU (Comics)

Which abbreviation for DCU? You can: 
- Pick a number 
- Hit return for the first item in the list (if any) 
- Or type the new value directly (separated with ', ' if it's a list)
Your choice? DCU

Which categories for DCU? You can: 
- Pick a number 
- Hit return for the first item in the list (if any) 
- Or type the new value directly (separated with ', ' if it's a list)
Your choice? comics/webcomics
```

The program will offer to save those choices for next time.

```
You chose:
original tags -> Batman - All Media Types 
preferred tags -> DCU (Comics), Batman - All Media Types
main tracking tag -> DCU (Comics) 
abbreviation -> DCU 
categories -> comics/webcomics
We can save these preferences for next time!
- No (hit return without typing anything)
- Yes (type anything then hit return)
Your choice?
```

If you choose to save them, it will offer up the option next time, like below.

```
Which preferred tags for Men's Hockey RPF? You can: 
- Pick a number 
- Hit return for the first item in the list (if any) 
- Or type the new value directly (separated with ', ' if it's a list)
0) Hockey RPF
Your choice?
```

### [3] Completing the metadata

You then need to edit the yaml file with any missing info. It also wouldn't hurt to double-check everything is named right so that the program will find all the files.

Note that the original ao3 tags might get shuffled.

### [4] Uploading and drafting

The goals here are to:
- Upload all the files to google drive and the internet archive
- Draft the ao3 post
- Save the dreamwidth html to a text file

#### Project identity

Terminal, blah blah, the same line changes if you're on Windows.

```shell
source .venv/bin/activate
python main.py post
```

This part will also ask for fandom abbreviation and project title and double check with you which folder the project is in.

```
Fandom abr: DCU
Full project title: Wayne Enterprises
Found a project folder! ../../../Musique/2.5 to post/dcu - we
You can:
- Use it (hit return without typing anything)
- Quit (type quit and then hit return)
- Use another folder (type the path to the folder then hit return)
Your choice? 
```

#### File editing and uploads

After that, it deals with the audio files, renaming them, adding cover art, and editing the metadata.

```
Renaming wip files... Done!
Adding cover art to mp3 files... Done!

Updating metadata...
../../../Musique/2.5 to post/dcu - we/[DCU] Wayne Enterprises.mp3
../../../Musique/2.5 to post/dcu - we/[DCU] Wayne Enterprises.wav
Done!
```

The next step is the upload to gdrive and will require you to switch to the pop up window the program automatically opens. Pick an account with some storage space and the right authorizations.

```
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?client_id=973588150329-lruivlpnrcfd3jes109dibm20rl9qepf.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&access_type=offline&response_type=code

Authentication successful.
Uploading podfic files to gdrive...
../../../Musique/2.5 to post/dcu - we/[DCU] Wayne Enterprises.mp3
Done!

Uploading podfic cover to gdrive...
../../../Musique/2.5 to post/dcu - we/we cover.png
Done!

Uploading podfic info to gdrive...
../../../Musique/2.5 to post/dcu - we/we metadata.yaml
Done!
```

Uploading to the internet archive doesn't require any action from you, but if an item with the same name already exists (because you tried to upload the podfic but stopped halfway through, or if another project has the same abbreviated identificator), the program will pause and check with you before going forward.

```
An item with the same name already exists (dcu-we)
You can:
- Add to the existing item (hit return)
- Choose a new identifier (input the chosen identifier)
Your choice? 
Uploading podfic files to ia...
200 - ../../../Musique/2.5 to post/dcu - we/[DCU] Wayne Enterprises.mp3
200 - ../../../Musique/2.5 to post/dcu - we/[DCU] Wayne Enterprises.wav
Done!

Uploading cover art to ia...
200 - ../../../Musique/2.5 to post/dcu - we/we cover.png
200 - ../../../Musique/2.5 to post/dcu - we/we cover.svg
Done!

Uploading podfic info to ia...
200 - ../../../Musique/2.5 to post/dcu - we/we metadata.yaml
Done!
```

#### Templates and draft

Then comes the html formatting and the ao3 draft.

```
Drafting podfic post to ao3... Creating ao3 template... Loging in to ao3... Done!
```

All these steps added new metadata (links, mostly) and so had to be executed before uplaoding the info files to gdrive/the internet archive.

```
Uploading podfic info to gdrive...
../../../Musique/2.5 to post/dcu - we/we metadata.yaml
Done!

Adding podfic link to ia... Done!

Uploading podfic info to ia...
200 - ../../../Musique/2.5 to post/dcu - we/we metadata.yaml
Done!
```

And lastly, the program prepares the dreamwidth html and adds it to the stockpiling file.

```
Creating dw template... saving in ../../../Musique/2.5 to post/dw.txt... Done!
```

### [5] Finishing up

- Double-check the ao3 draft and hit post
- Cross-post to dreamwidth if you want
- Add the work to your tracker (this part isn't automated yet)

TODO due to a bug, the pairing categories are never filled out. Also, figure out how to lock works...

## Code

 ### post

- AudioHandler
    -> init: id, files, metadata
    -> add_cover_art
    -> rename_wip_audio_files
    -> update_metadata
    -> save_audio_length
- GDriveUploader
    -> init: id, files, metadata
    -> upload_cover
    -> upload_metadata
    -> upload_audio
    -> upload_file
- IAUploader
    -> init: id, files, metadata
    -> upload_cover
    -> upload_metadata
    -> upload_audio
    -> upload_file
    -> update_description
- Ao3Drafter
    -> init: id, files, metadata
    -> draft_podfic
- DWPoster
    -> init: id, files, metadata
    -> save_dw_post_text: mass_xpost=True
- Ao3Template
    -> init: id, files, metadata
    - summary
    - work_text
- DWTemplate
    -> init: metadata
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
