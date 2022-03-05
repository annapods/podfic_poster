# -*- coding: utf-8 -*-
"""
Filling ao3 and dw posting templates
TODO tracker
"""


### Aux functions

def delete_empty(items):
    return [i for i in items if i]

def get_a_href(link, text):
    return f'''<a href="{link}">{text}</a>'''

def get_enum(items):
    if not items: return ""
    if len(items) == 1: return items[-1]
    if len(items) == 2: return f"{items[-2]} and {items[-1]}"
    else: return ', '.join(items[:-3] + [f"{items[-2]} and {items[-1]}"])

def get_enum_links(items):
    if not items: return ""
    return get_enum([get_a_href(link, text) for link, text in items])

def get_img(link="", width=0, height=0):
    if link: template = f'''<img src="{link}"'''
    else: template = f'''<img src="COVER"'''
    if width: template += f' width="{width}"'
    if height: template += f' height="{height}"'
    if link: template += f''' alt="cover art" />'''
    else: template += f''' alt="cover art welcome" />'''
    return template

def get_li(items):
    if items: return "\n".join([f'''<li>{item}</li>''' for item in items])
    else: return ""


### DW

class DWTemplate:
    
    def __init__(self, info, verbose=True):
        self._verbose = verbose
        self.info = info
        self.post = self.get_post()
        self.save_as = ""

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def get_post(self):
        post = '<div style="text-align: center;">' \
        + get_img(self.info["IA Cover Link"], width=200, height=200) + "</div>" \
        + "\n\n" \
        + f'''<p><strong>Parent works:</strong> {get_enum_links(zip(self.info["Parent Work URL"], self.info["Parent Work Title"]))}</a><br>''' \
        + f'''<p><strong>Writers:</strong> {get_enum_links(self.info["Writer"])}<br>''' \
        + f'''<strong>Readers:</strong> {get_enum_links(self.info["Creator/Pseud(s)"])}<br>''' \
        + f'''<strong>Occasion:</strong> {self.info["Occasion"]}<br>''' \
        + f'''<strong>Fandoms:</strong> {', '.join(self.info['Fandoms'])}<br>''' \
        + f'''<strong>Pairings:</strong> {', '.join(self.info['Relationships'])}<br>''' \
        + f'''<strong>Characters:</strong> {', '.join(self.info['Characters'])}<br>''' \
        + f'''<strong>Tags:</strong> {', '.join(self.info['Additional Tags'])}<br>''' \
        + f'''<strong>Rating:</strong> {self.info['Rating']}<br>''' \
        + f'''<strong>Content notes:</strong> {self.info['Content Notes']}<br>''' \
        + f'''<strong>Credits:</strong> {get_enum_links(self.info['Credits'])}<br>''' \
        + f'''<strong>Length (including endnotes):</strong> {self.info['Audio Length']}<br>''' \
        + f'''<strong>Summary:</strong> {self.info['Summary']}</p>'''
        links = [
            (self.info["Podfic Link"], "ao3"),
            (self.info["IA Link"], "internet archive"),
            (self.info["GDrive Link"], "gdrive")
        ]
        post += f'''\n\n<p><strong>Link to podfic:</strong> {get_enum_links(links)}'''
        return post



class Ao3Template:
    """
    Filling the ao3 template
    """
    def __init__(self, info, verbose=True):
        self._verbose = verbose
        self.info = info
        self.summary = self.get_ao3_summary()
        self.work_text = self.get_ao3_work_text()

    def _vprint(self, string, end="\n"):
        """ Print if verbose """
        if self._verbose:
            print(string, end=end)

    def get_ao3_summary(self):
        """
        Blah blah summary.

        00:00:00 :: Written by <a href="link">writer</a>.
        """
        summary = self.info["Summary"]
        if self.info["Audio Length"] not in summary:
            summary = f'''{summary}\n\n{self.info["Audio Length"]}'''
        if self.info["Writer"] and " :: Written by " not in summary:
            authors = get_enum_links(self.info["Writer"])
            summary =  f'''{summary} :: Written by {authors}.'''
        return summary

    def get_section(self, title:str, parts:list):
        """
        Big sections
        """
        template = ""
        parts = delete_empty(parts)
        if parts: template = f"<h3>{title}:</h3>\n" \
        + "\n\n".join(parts)
        return template

    def get_sub_section(self, title:str, content:str):
        """
        Sub sections of big sections
        """
        template = ""
        if content: template = f'''<p><strong>{title}:</strong><br>\n''' \
        + content + "</p>"
        return template
        
    def get_ia_dl(self):
        title = get_a_href(self.info["IA Link"], "Internet archive")
        content = "Mp3 and raw audio files for download and streaming as well as the html text and the cover art " \
        + "in png and svg formats if applicable.\n" \
        + "<br>See the side of the page (“download options”) for the different formats/files and for" \
        + "download. The mp3 file will be under “VBR MP3”.</p>"
        return self.get_sub_section(title, content)

    def get_gdrive_dl(self):
        title = get_a_href(self.info["GDrive Link"], "Google drive")
        content = "Mp3 file(s) streamable on gdrive.</p>"
        return self.get_sub_section(title, content)

    def get_streaming(self):
        content = "<br>\n".join(
            [f'''<audio src="{link}"></audio>''' for link in self.info["IA Streaming Links"]])
        return self.get_sub_section("Browser streaming", content)

    def get_audio_files(self):
        parts = [
            self.get_ia_dl(),
            self.get_gdrive_dl(),
            self.get_streaming()
        ]
        return self.get_section("Podfic files", parts)

    def get_context(self):
        occasion = self.info["Occasion"]
        content = "" if occasion == "none" or occasion == "n/a" else f'''This was created for {occasion}.'''
        return self.get_sub_section("Context", content)

    def get_thanks(self):
        content = ""
        if self.info["Writer"]:
            content = f'''Thanks to {get_enum_links(self.info["Writer"])} for '''
            thanks = "giving blanket permission to podfics" if self.info["BP"] else "giving me permission to record this work!"
            content += thanks
        return self.get_sub_section("Thanks", content)

    def get_additional_credits(self):
        credits = self.info["Credits"]
        if self.info["Stickers"]:
            credits.append((
                "https://www.dropbox.com/sh/m594efbyu3kjrse/AACKZKGpiS0UqQZIdTXFSKoSa?dl=0",
                "lemon rating stickers"
            ))
        if credits:
            credits = [get_a_href(link, name) for link, name in credits]
        content = get_li(credits)
        return self.get_sub_section("Additional credits", content)

    def get_content_notes(self):
        return self.get_sub_section("Content notes", self.info["Content Notes"])

    def get_notes(self):
        parts = [
            self.get_context(),
            self.get_thanks(),
            self.get_additional_credits(),
            self.get_content_notes()
        ]
        return self.get_section("Notes", parts)

    def get_contact_info(self):
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
        info["socials"] = get_enum_links(info["socials"])
        info = [f'''{key}: {value}''' for key, value in info.items()]
        content = get_li(info)
        return self.get_sub_section("Contact info", content)

    def get_what_to_say(self):
        content = [
            'I’d love to hear from you! Be it a single word or emoji, a long freetalk on your thoughts and feelings, recs for things to read or listen to that you think I might like, meta, further transformative works, ...',
            'I will love you forever: “this is how I experienced this work”, “you might be interested by this other tool or method”, “you kind of fucked up there on that front”, “I have some concrit on this aspect, would you be interested in hearing it?”',
            'I will still like you but it’s going to be awkward: “I think you should change the way you do things to fit my own preferences”, “I usually don’t like this thing, but you’re not like other podficcers”, “I loved so and so about the writing that you didn’t write and this comment is really for the writer”.',
            'Some super useful podfic feedback tools by Mo: <a href="https://yue-ix.dreamwidth.org/144236.html">how to</a> and <a href="https://podfic-tips.livejournal.com/95933.html">vocabulary</a>'
        ]
        content = "<br>\n".join(content)
        return self.get_sub_section("What to say/what not to say", content)

    def get_reply_policy(self):
        content = "Leaving me comments is kind of like starting a snail mail exchange in reply to a message in a bottle. I might not answer quickly (as in, it… could take me a few months…) but I will eventually!"
        return self.get_sub_section("When to expect a reply", content)

    def get_feedback(self):
        parts = [
            self.get_contact_info(),
            self.get_what_to_say(),
            self.get_reply_policy()
        ]
        return self.get_section("Feedback", parts)

    def get_cover_art(self):
        content = f'''<p align="center">{get_img(self.info["IA Cover Link"], width=250)}'''
        if self.info["Cover Artist"]:
            content += f'''<br>\nCover art by {get_enum_links(self.info["Cover Artist"])}'''
        content += "</p>"
        return content

    def get_ao3_work_text(self):
        parts = [
            self.get_cover_art(),
            self.get_audio_files(),
            self.get_notes(),
            self.get_feedback()
        ]
        parts = [part for part in parts if parts]
        return "\n\n<p>&nbsp;</p>\n\n".join(parts)