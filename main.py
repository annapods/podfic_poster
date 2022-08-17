# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from project_handler import ProjectHandler


if __name__ == "__main__":
    parser = ArgumentParser(description="Podfic posting helper!")
    parser.add_argument('mode', help="new or post?", choices=['new', 'post'])
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    parser.add_argument('--link', help="link to the ao3 work", default=None)
    parser.add_argument('--fandom', help="abreviation of the fandom " + \
        "(like at the start of the mp3 file name)", default=None)
    parser.add_argument('--title', help="title of the work", default=None)
    args = parser.parse_args()

    verbose = not args.quiet

    if args.mode == "new":
        handle = ProjectHandler(
            link=args.link, fandom_abr=args.fandom, raw_title=args.title,
            mode="extract", verbose=verbose)

    if args.mode == "post":
        handle = ProjectHandler(
            link=args.link, fandom_abr=args.fandom, raw_title=args.title,
            mode="saved", verbose=verbose)
        handle.post()
