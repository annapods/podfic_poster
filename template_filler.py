# pylint: disable=multiple-statements
# pylint: disable=invalid-name
# pylint: disable=global-statement
# -*- coding: utf-8 -*-
"""
Filling ao3 and dw posting templates
TODO tracker
"""

from typing import List, Tuple
from gettext import translation
from base_object import VerboseObject
from project_metadata import remove_placeholder_links, not_placeholder_link


# Language set in __init__ to this global variable
# Couldn't figure out how to make xgettext find the right keyword with it as an instance
# attribute
def i18l(_:str) -> str:
    """ Placeholder """
    return "NOPE, gotta debug, sorry!"


class Template(VerboseObject):
    """ Auxiliary html-coding functions and setting the locale """

    def __init__(self, lang:str, verbose:bool=True):
        super().__init__(verbose)
        translator = translation('template_filler', localedir='.locales', languages=[lang])
        global i18l
        i18l = translator.gettext

    @staticmethod
    def delete_empty(items:List) -> List:
        """ Delete empty items in list """
        return [i for i in items if i]

    @staticmethod
    def get_a_href(link:str, text:str) -> str:
        """ Formats link and text into an html hyperlink """
        return f'''<a href="{link}">{text}</a>'''

    @staticmethod
    def get_enum(items:List, conj:str="") -> str:
        """ Joins items in a string with commas and 'and' """
        if not items: return ""
        if len(items) == 1: return items[-1]
        conj = i18l(conj) if conj else i18l("and")
        if len(items) == 2: return " ".join([items[-2], conj, items[-1]])
        return ', '.join(items[:-2] + [" ".join([items[-2], conj, items[-1]])])

    @staticmethod
    def get_enum_links(items:List[Tuple[str, str]]) -> str:
        """ Formats items into a string of hyperlinks """
        if not items: return ""
        return Template.get_enum([Template.get_a_href(link, text) for link, text in items])

    @staticmethod
    def get_img(link:str="", width:int=0, height:int=0,
        img_alt_text:str="",
        no_img_alt_text:str="")-> str:
        """ Formats info into the html for an embedded image """
        template = f'''<img src="{link}"''' if link else '''<img src="COVER"'''
        if width: template += f' width="{width}"'
        if height: template += f' height="{height}"'
        if link: template += f''' alt="{img_alt_text}" />'''
        else: template += f''' alt="{no_img_alt_text}" />'''
        return template

    @staticmethod
    def add_tag(tag:str, string:str) -> str:
        """ Encloses the string in the html tag """
        return f"<{tag}>{string}</{tag}>"

    @staticmethod
    def get_li(items:List[str]) -> str:
        """ Formats items into the html code for an <li> list """
        if items: return Template.add_tag(
            "ul", "".join([f'''<li>{item}</li>''' for item in items]))
        return ""

### DW

class DWTemplate(Template):
    """ DW template creator! """

    def __init__(self, metadata, verbose:bool=True):
        super().__init__(metadata["Language"], verbose)
        self._info = metadata
        self.post_text = self._get_post()

    def _get_post(self) -> str:
        """ Formats the dw post html """

        def heading(header):
            """ Formats a dw info header """
            return self.add_tag("str", (header+i18l(':')))+" "
        
        def heading_if_links(head:str, links:List[Tuple[str,str]], ending:str="") -> str:
            """ Creates the header + content string if the link isn't a placeholder """
            links = remove_placeholder_links(links)
            if links:
                return heading(head) + self.get_enum_links(links) + ending

        cover = '<div style="text-align: center;">' \
            + self.get_img(self._info["IA Cover Link"], width=200, height=200,
            img_alt_text=i18l("Cover art."), no_img_alt_text=i18l("Cover art welcome.")) \
            + "</div>"

        infos = [
                heading_if_links("Parent works",
                    zip(self._info["Parent Work URL"], self._info["Parent Work Title"])),
                heading_if_links(i18l("Writers"), self._info["Writers"]),
                heading_if_links(i18l("Readers"), self._info["Creator/Pseud(s)"]),
                heading(i18l("Context")) + self._info["Occasion"],
                heading(i18l("Fandoms")) + ', '.join(self._info['Fandoms']),
                heading(i18l("Pairings")) + ', '.join(self._info['Relationships']),
                heading(i18l("Characters")) + ', '.join(self._info['Characters']),
                heading(i18l("Tags")) + ', '.join(self._info['Additional Tags']),
                heading(i18l("Rating")) + self._info['Rating'],
                heading(i18l("Content notes")) + self._info['Content Notes'],
                heading_if_links(i18l("Additional credits"), self._info['Credits']),
                heading(i18l("Audio length (incl. potential endnotes)")) \
                    + self._info['Audio Length'],
                heading(i18l("Summary")) + self._info['Summary']
            ]
        infos = [item for item in infos if item]
        info = self.add_tag("p", "<br>".join(infos))

        links = self.add_tag("p",
            heading_if_links(i18l("Link to podfics"), [
                (self._info["Podfic Link"], "ao3"),
                (self._info["IA Link"], "internet archive"),
                (self._info["GDrive Link"], "gdrive")
        ]))

        post = "\n\n".join([cover, info, links])
        return post

### Ao3

class Ao3Template(Template):
    """ Filling the ao3 template """

    def __init__(self, metadata, verbose:bool=True):
        super().__init__(metadata["Language"], verbose)
        self._info = metadata
        self.summary = self._get_ao3_summary()
        self.work_text = self._get_ao3_work_text()

    def _get_ao3_summary(self) -> str:
        """ Formats the ao3 summary html:
        Blah blah summary.
        00:00:00 :: Written by <a href="link">writer</a>. """
        summary = self._info["Summary"]
        # Check if summary is the parent work's or if it has been edited for the podfic already
        # This is (clumsily) done using the audio length
        if self._info["Audio Length"] not in summary:
            summary += f'\n\n{self._info["Audio Length"]}'
            links = remove_placeholder_links(self._info["Writers"])
            if links:
                summary += ' :: '
                summary += i18l("Written by")+" "+self.get_enum_links(self._info["Writers"])+'.'
        return summary

    def _get_section(self, title:str, subsections:List[str]) -> str:
        """ Big sections, potentialy several subsections
        Returns an empty string if no subsections are given """
        subsections = "\n\n".join(self.delete_empty(subsections))
        if not subsections: return ""
        return self.add_tag("h3", title+i18l(':')) + "\n" + subsections

    def _get_sub_section(self, title:str, content:str) -> str:
        """ Sub sections of big sections
        Returns an empty string if there's no content to put in the section """
        if not content: return ""
        if content.startswith("<li>"):  # an attempt at fixing whatever happens to
            # <li> formatting somewhere between yaml and ao3...
            template = self.add_tag("p",
                self.add_tag("strong", title+i18l(':')
                ) + content
            )
        else:
            template = self.add_tag("p",
                self.add_tag("strong",
                    title+i18l(':')
                ) + "<br>" + content
            )
        return template


    def _get_ia_dl(self) -> str:
        """ Internet archive section """
        title = self.get_a_href(self._info["IA Link"], "Internet archive")
        content = i18l("Mp3 and raw audio files for download and streaming as well as " \
            + "any other files relevant to this work. " \
            + 'See the side of the page ("download options") for the different formats/files. ' \
            + 'The mp3 will be under "VBR MP3".')
        return self._get_sub_section(title, content)

    def _get_gdrive_dl(self) -> str:
        """ GDrive section """
        title = self.get_a_href(self._info["GDrive Link"], "Google drive")
        content = i18l("Mp3 file(s) to stream or download on gdrive.")
        return self._get_sub_section(title, content)

    def _get_streaming(self) -> str:
        """ Streaming section """
        content = "<br>\n".join(
            [f'''<audio src="{link}"></audio>''' for link in self._info["IA Streaming Links"]])
        return self._get_sub_section(i18l('Browser streaming'), content)

    def _get_audio_files(self) -> str:
        """ Audio files section """
        parts = [
            self._get_ia_dl(),
            self._get_gdrive_dl(),
            self._get_streaming()
        ]
        return self._get_section(i18l("Podfic files"), parts)

    def _get_context(self) -> str:
        """ Context section """
        occasion = self._info["Occasion"]
        content = "" if occasion in ["none", "n/a"] else \
            i18l("This was created for")+" "+occasion+"."
        return self._get_sub_section(i18l("Context"), content)

    def _get_thanks(self) -> str:
        """ Thanks section """
        if not self._info["Writers"]:
            return ""
        reason = i18l("for giving blanket permission to podfics!") if self._info["BP"] \
            else i18l("for letting me record this work!")
        content = " ".join([
            i18l("Thanks to"),
            self.get_enum_links(self._info["Writers"]),
            reason])
        return self._get_sub_section(i18l("Thanks"), content)

    def _get_additional_credits(self) -> str:
        """ Credits section """
        credit = self._info["Credits"]
        if self._info["Stickers"]:
            credit.append([
                "https://www.dropbox.com/sh/m594efbyu3kjrse/AACKZKGpiS0UqQZIdTXFSKoSa?dl=0",
                i18l("Lemon rating stickers")
            ])
        if credit:
            credit = [self.get_a_href(link, name) for link, name in credit \
                if not_placeholder_link(link, name)]
        content = self.get_li(credit)
        return self._get_sub_section(i18l("Additional credits"), content)

    def _get_content_notes(self) -> str:
        """ Content notes section """
        return self._get_sub_section(i18l("Content notes"), self._info["Content Notes"])

    def _get_notes(self) -> str:
        """ Notes section """
        parts = [
            self._get_context(),
            self._get_thanks(),
            self._get_additional_credits(),
            self._get_content_notes()
        ]
        return self._get_section(i18l("Notes"), parts)

    def _get_contact_info(self) -> str:
        """ Contact info section
        NOTE contact info is hardcoded, could it be adapted? """
        info = {
            i18l("Names"): self.get_enum(["Anna", "Annapods"], i18l("or")),
            i18l("Pronouns"): i18l("she or they"),
            i18l("Socials"): self.get_enum_links([
                ("https://twitter.com/iamapodperson", "twitter"),
                ("http://annapods.tumblr.com/", "tumblr"),
                ("https://annapods.dreamwidth.org/", "dreamwidth")
            ]),
            i18l("Email"): "annabelle.myrt@gmail.com"
        }
        info = [f'''{key}{i18l(":")} {value}''' for key, value in info.items()]
        content = self.get_li(info)
        return self._get_sub_section(i18l("Contact info"), content)

    def _get_what_to_say(self) -> str:
        """ What to say section """
        return self._get_sub_section(i18l("What to say/not to say"),
            i18l(
            "I'd love to hear from you! Be it a single word or emoji, a long freetalk on your " \
                + 'thoughts and feelings, recs for things to read or listen to that you think ' \
                + 'I might like, meta, further transformative works, ...<br>\n' \
            + 'I will love you forever: "this is how I experienced this work", "you might be ' \
                + 'interested by this other tool or method", "you kind of fucked up there on ' \
                + 'that front", "I have some concrit on this aspect, would you be interested ' \
                + 'in hearing it?"<br>\n' \
            + '''I will still like you but it's going to be awkward: "I think you should ''' \
                + '''change the way you do things to fit my own preferences", "I usually ''' \
                + '''don't like this thing, but you're not like other podficcers", "I loved ''' \
                + '''so and so about the writing that you didn't write and this comment is ''' \
                + '''really for the writer".<br>\n''' \
            + 'Some super useful podfic feedback tools by Mo: ''' \
                + '''<a href="https://yue-ix.dreamwidth.org/144236.html">how to</a> and ''' \
                + '''<a href="https://podfic-tips.livejournal.com/95933.html">vocabulary</a>'''
            ))

    def _get_reply_policy(self) -> str:
        """ Reply policy section """
        return self._get_sub_section(i18l("When to expect a reply"),
            i18l("Leaving me comments is kind of like starting a snail mail " \
            + "exchange in reply to a message in a bottle. I might not answer quickly (as in, " \
            + "it could take me... a couple of years...) but I will eventually!"))

    def _get_feedback(self) -> str:
        """ Feedback section """
        parts = [
            self._get_contact_info(),
            self._get_what_to_say(),
            self._get_reply_policy()
        ]
        return self._get_section(i18l("Feedback"), parts)

    def _get_cover_art(self) -> str:
        """ Cover art """
        content = f'''<p align="center">{self.get_img(self._info["IA Cover Link"], width=250,
            img_alt_text=i18l("Cover art."), no_img_alt_text=i18l("Cover art welcome."))}'''
        if not_placeholder_link(*(self._info["Cover Artist(s)"][0])):
            content += f'''<br>\n{i18l("Cover art by")} ''' \
                + self.get_enum_links(self._info["Cover Artist(s)"])
        content += "</p>"
        return content

    def _get_ao3_work_text(self) -> str:
        """ Format and return the whole of the work text """
        parts = [
            self._get_cover_art(),
            self._get_audio_files(),
            self._get_notes(),
            self._get_feedback()
        ]
        parts = [part for part in parts if parts]
        # return "\n\n<p>&nbsp;</p>\n\n".join(parts)
        return "\n\n\n".join(parts)
