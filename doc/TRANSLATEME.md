# Notes on internationalisation

A few tutos: [1](https://simpleit.rocks/python/how-to-translate-a-python-project-with-gettext-the-easy-way/)

## Variables and structure

Gettext is a little like Django in the sense that it relies on a pretty specific files structure, and if you break it then good luck with debugging.

Root directory of translation files: `DIR=.locales`

In it, one folder per language, named with the language **code**. Gettext can find the code from the full name (ex: English -> en_US), but using the actual name won't work. So: `LANG=fr`

In a language folder, a subfolder named `LC_MESSAGES`. Not sure why but it looks like a convention.

Translations can be organized in domains. This is useful for big translation projects, or for subprojects. Here, for now, we only have the template stuff, but if we wanted to translate the cli, we'd set up a second domain. So: `DOMAIN=template_filler`

## Generating the template .pot file

Xgettext can gather all the keys used in a file (or files) and create a template translation file:
```shell
FILE=src/template_filler.py
xgettext -d $DOMAIN --keyword=i18l -o $DIR/$DOMAIN.pot $FILE --from-code=UTF-8
```

A few explanations:
- `--keyword=i18l` tells it what to look for. It'll gather all* the strings passed as arguments to that keyword, for ex in `i18l("Translate translate")`.
- *xgettext can't seem to find those calls in f-strings.
- `--from-code=UTF-8` doesn't work, might have to change it by hand, from `charset=CHARSET` to `charset=UTF-8`.

## Adding a new language

The .pot file is to be used as a template, just copy paste it in the new language folder then fill that copy: `cp $DIR/$DOMAIN.pot $DIR/$LANG/LC_MESSAGES/$DOMAIN.po`

Gettext is iiuc written in C or C++, so it needs a compiled binary file: `msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po`

## Updating after changes

Just overwrite the template file, it shouldn't have been edited anyway: `xgettext -d $DOMAIN --keyword=i18l -o $DIR/$DOMAIN.pot template_filler.py`

Then it can be merged with the existing translation files without damaging them: `msgmerge --update $DIR/$LANG/LC_MESSAGES/$DOMAIN.po $DIR/$DOMAIN.pot`

Translate the new sentences (and potentially delete the unused ones? not sure), then compile again: `msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po`

Done!

# TL;DR

## Setup
```shell
DIR=.locales
DOMAIN=template_filler
```

## If you change the strings in the i18l function in `src/template_filler.py`
```shell
FILE=src/template_filler.py
xgettext -d $DOMAIN --keyword=i18l -o $DIR/$DOMAIN.pot $FILE --from-code=UTF-8
```
Open the .pot file and change `charset=CHARSET` to `charset=UTF-8`.
For each language, get the language code, replace `fr` with that code.
```shell
LANG=fr
msgmerge --update $DIR/$LANG/LC_MESSAGES/$DOMAIN.po $DIR/$DOMAIN.pot
```
Go to next section.

## If you update a translation
Update the .po file with translations.
Get the language code, replace `fr` with that code.
```shell
LANG=fr
msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po
```

## If you want to add a language
Get the language code and replace `fr` with that code.
```shell
LANG=fr
cp $DIR/$DOMAIN.pot $DIR/$LANG/LC_MESSAGES/$DOMAIN.po
```
Fill the template.
```shell
msgfmt -o $DIR/$LANG/LC_MESSAGES/$DOMAIN.mo $DIR/$LANG/LC_MESSAGES/$DOMAIN.po
```
