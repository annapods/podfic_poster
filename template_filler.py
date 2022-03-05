# pylint: disable=multiple-statements
# -*- coding: utf-8 -*-
"""
Filling ao3 and dw posting templates
TODO tracker
"""


class TemplateAux:
    """ Auxiliary html-coding functions """

    @staticmethod
    def delete_empty(items):
        """ Delete empty items in list """
        return [i for i in items if i]

    @staticmethod
    def get_a_href(link, text):
        """ Formats link and text into an html hyperlink """
        return f'''<a href="{link}">{text}</a>'''

    @staticmethod
    def get_enum(items):
        """ Joins items in a string with commas and 'and' """
        if not items: return ""
        if len(items) == 1: return items[-1]
        if len(items) == 2: return f"{items[-2]} and {items[-1]}"
        return ', '.join(items[:-3] + [f"{items[-2]} and {items[-1]}"])

    @staticmethod
    def get_enum_links(items):
        """ Formats items into a string of hyperlinks """
        if not items: return ""
        return TemplateAux.get_enum([TemplateAux.get_a_href(link, text) for link, text in items])

    @staticmethod
    def get_img(link="", width=0, height=0):
        """ Formats info into the html for an embedded image """
        template = f'''<img src="{link}"''' if link else '''<img src="COVER"'''
        if width: template += f' width="{width}"'
        if height: template += f' height="{height}"'
    
        if link: template += ''' alt="cover art" />'''
        else: template += ''' alt="cover art welcome" />'''

        return template

    @staticmethod
    def get_li(items):
        """ Formats items into the html code for an <li> list """
        if items: return "\n".join([f'''<li>{item}</li>''' for item in items])
        else: return ""


### DW

class DWTemplate:
    """ DW template creator! """
    
    def __init__(self, info, verbose=True):
        """ info is the dict of work info, not the WorkInfo object itself """
        self._verbose = verbose
        self._info = info
        self.post = self._get_post()

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def _get_post(self):
        """ Formats the dw post html """
        post = '<div style="text-align: center;">' \
        + TemplateAux.get_img(self._info["IA Cover Link"], width=200, height=200) + "</div>" \
        + "\n\n" \
        + f'''<p><strong>Parent works:</strong> ''' \
        + TemplateAux.get_enum_links(
            zip(self._info["Parent Work URL"], self._info["Parent Work Title"])) \
        + '''</a><br>''' \
        + '''<p><strong>Writers:</strong> ''' \
        + TemplateAux.get_enum_links( self._info["Writer"]) \
        + '''<br>''' \
        + '''<strong>Readers:</strong> ''' \
        + TemplateAux.get_enum_links(self._info["Creator/Pseud(s)"]) \
        + '''<br>''' \
        + f'''<strong>Occasion:</strong> {self._info["Occasion"]}<br>''' \
        + f'''<strong>Fandoms:</strong> {', '.join(self._info['Fandoms'])}<br>''' \
        + f'''<strong>Pairings:</strong> {', '.join(self._info['Relationships'])}<br>''' \
        + f'''<strong>Characters:</strong> {', '.join(self._info['Characters'])}<br>''' \
        + f'''<strong>Tags:</strong> {', '.join(self._info['Additional Tags'])}<br>''' \
        + f'''<strong>Rating:</strong> {self._info['Rating']}<br>''' \
        + f'''<strong>Content notes:</strong> {self._info['Content Notes']}<br>''' \
        + '''<strong>Credits:</strong> ''' \
        + TemplateAux.get_enum_links(self._info['Credits']) \
        + '''<br>''' \
        + f'''<strong>Length (including endnotes):</strong> {self._info['Audio Length']}<br>''' \
        + f'''<strong>Summary:</strong> {self._info['Summary']}</p>'''
        links = [
            (self._info["Podfic Link"], "ao3"),
            (self._info["IA Link"], "internet archive"),
            (self._info["GDrive Link"], "gdrive")
        ]
        post += f'''\n\n<p><strong>Link to podfic:</strong> {TemplateAux.get_enum_links(links)}'''
        return post



class Ao3Template:
    """ Filling the ao3 template """

    def __init__(self, info, verbose=True):
        self._verbose = verbose
        self._info = info
        self.summary = self._get_ao3_summary()
        self.work_text = self._get_ao3_work_text()

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def _get_ao3_summary(self):
        """ Formats the ao3 summary html:
        
        Blah blah summary.

        00:00:00 :: Written by <a href="link">writer</a>. """

        summary = self._info["Summary"]
        if self._info["Audio Length"] not in summary:
            summary = f'''{summary}\n\n{self._info["Audio Length"]}'''
        if self._info["Writer"] and " :: Written by " not in summary:
            authors = TemplateAux.get_enum_links(self._info["Writer"])
            summary =  f'''{summary} :: Written by {authors}.'''
        return summary

    def _get_section(self, title:str, parts:list):
        """ Big sections """
        template = ""
        parts = TemplateAux.delete_empty(parts)
        if parts: template = f"<h3>{title}:</h3>\n" \
        + "\n\n".join(parts)
        return template

    def _get_sub_section(self, title:str, content:str):
        """ Sub sections of big sections """
        template = ""
        if content: template = f'''<p><strong>{title}:</strong><br>\n''' \
        + content + "</p>"
        return template
        
    def _get_ia_dl(self):
        """ Internet archive section """
        title = TemplateAux.get_a_href(self._info["IA Link"], "Internet archive")
        content = "Mp3 and raw audio files for download and streaming as well as the html text " \
        + "and the cover art in png and svg formats if applicable.\n" \
        + "<br>See the side of the page (“download options”) for the different formats/files " \
        + "and for download. The mp3 file will be under “VBR MP3”.</p>"
        return self._get_sub_section(title, content)

    def _get_gdrive_dl(self):
        """ GDrive section """
        title = TemplateAux.get_a_href(self._info["GDrive Link"], "Google drive")
        content = "Mp3 file(s) streamable on gdrive.</p>"
        return self._get_sub_section(title, content)

    def _get_streaming(self):
        """ Streaming section """
        content = "<br>\n".join(
            [f'''<audio src="{link}"></audio>''' for link in self._info["IA Streaming Links"]])
        return self._get_sub_section("Browser streaming", content)

    def _get_audio_files(self):
        """ Audio files section """
        parts = [
            self._get_ia_dl(),
            self._get_gdrive_dl(),
            self._get_streaming()
        ]
        return self._get_section("Podfic files", parts)

    def _get_context(self):
        """ Context section """
        occasion = self._info["Occasion"]
        content = "" if occasion == "none" or occasion == "n/a" else f'''This was created for {occasion}.'''
        return self._get_sub_section("Context", content)

    def _get_thanks(self):
        """ Thanks section """
        content = ""
        if self._info["Writer"]:
            content = f'''Thanks to {TemplateAux.get_enum_links(self._info["Writer"])} for '''
            thanks = "giving blanket permission to podfics" if self._info["BP"] \
                else "giving me permission to record this work!"
            content += thanks
        return self._get_sub_section("Thanks", content)

    def _get_additional_credits(self):
        """ Credits section """
        credits = self._info["Credits"]
        if self._info["Stickers"]:
            credits.append((
                "https://www.dropbox.com/sh/m594efbyu3kjrse/AACKZKGpiS0UqQZIdTXFSKoSa?dl=0",
                "lemon rating stickers"
            ))
        if credits:
            credits = [TemplateAux.get_a_href(link, name) for link, name in credits]
        content = TemplateAux.get_li(credits)
        return self._get_sub_section("Additional credits", content)

    def _get_content_notes(self):
        """ Content notes section """
        return self._get_sub_section("Content notes", self._info["Content Notes"])

    def _get_notes(self):
        """ Notes section """
        parts = [
            self._get_context(),
            self._get_thanks(),
            self._get_additional_credits(),
            self._get_content_notes()
        ]
        return self._get_section("Notes", parts)

    def _get_contact_info(self):
        """ Contact info section """
        info = {
            "names": "Anna or Annapods",
            "pronouns": "she or they",
            "socials": [
                ("https://twitter.com/iamapodperson", "twitter"),
                ("http://annapods.tumblr.com/", "tumblr"),
                ("https://annapods.dreamwidth.org/", "dreamwidth")
            ],
            "email": "annabelle.myrt@gmail.com"
        }
        info["socials"] = TemplateAux.get_enum_links(info["socials"])
        info = [f'''{key}: {value}''' for key, value in info.items()]
        content = TemplateAux.get_li(info)
        return self._get_sub_section("Contact info", content)

    def _get_what_to_say(self):
        """ What to say section """
        content = [
            'I’d love to hear from you! Be it a single word or emoji, a long freetalk on your ' \
                + 'thoughts and feelings, recs for things to read or listen to that you think ' \
                + 'I might like, meta, further transformative works, ...',
            'I will love you forever: “this is how I experienced this work”, “you might be ' \
                + 'interested by this other tool or method”, “you kind of fucked up there on ' \
                + 'that front”, “I have some concrit on this aspect, would you be interested ' \
                + 'in hearing it?”',
            'I will still like you but it’s going to be awkward: “I think you should change ' \
                + 'the way you do things to fit my own preferences”, “I usually don’t like ' \
                + 'this thing, but you’re not like other podficcers”, “I loved so and so ' \
                + 'about the writing that you didn’t write and this comment is really for the ' \
                + 'writer”.',
            'Some super useful podfic feedback tools by Mo: <a href="https://yue-ix.dreamwidth' \
                + '.org/144236.html">how to</a> and <a href="https://podfic-tips.livejournal.' \
                + 'com/95933.html">vocabulary</a>'
        ]
        content = "<br>\n".join(content)
        return self._get_sub_section("What to say/what not to say", content)

    def _get_reply_policy(self):
        """ Reply policy section """
        content = "Leaving me comments is kind of like starting a snail mail exchange in reply to a message in a bottle. I might not answer quickly (as in, it… could take me a few months…) but I will eventually!"
        return self._get_sub_section("When to expect a reply", content)

    def _get_feedback(self):
        """ Feedback section """
        parts = [
            self._get_contact_info(),
            self._get_what_to_say(),
            self._get_reply_policy()
        ]
        return self._get_section("Feedback", parts)

    def _get_cover_art(self):
        """ Cover art """
        content = f'''<p align="center">{TemplateAux.get_img(self._info["IA Cover Link"],
            width=250)}'''
        if self._info["Cover Artist"]:
            content += f'''<br>\nCover art by {TemplateAux.get_enum_links(self._info["Cover Artist"])}'''
        content += "</p>"
        return content

    def _get_ao3_work_text(self):
        """ Format and return the whole of the work text """
        parts = [
            self._get_cover_art(),
            self._get_audio_files(),
            self._get_notes(),
            self._get_feedback()
        ]
        parts = [part for part in parts if parts]
        return "\n\n<p>&nbsp;</p>\n\n".join(parts)