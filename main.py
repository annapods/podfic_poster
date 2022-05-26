# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from project_handler import ProjectHandler


if __name__ == "__main__":
    parser = ArgumentParser(description="Podfic posting helper!")
    parser.add_argument('mode', help="new or post?", choices=['new', 'post'])
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    args = parser.parse_args()

    verbose = not args.quiet

    if args.mode == "new":
        handle = ProjectHandler(
            link="https://archiveofourown.org/works/37243984", fandom_abr="HRPF", raw_title="I want to believe",
            mode="extract", verbose=verbose)

    if args.mode == "post":
        handle = ProjectHandler(
            # fandom_abr="HRPF", raw_title="It’s so late, but my brain won’t sleep",
            mode="saved", verbose=verbose)
        handle.post()
