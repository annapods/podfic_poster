# -*- coding: utf-8 -*-
""" Command line program """

from argparse import ArgumentParser
from sys import exit
from cli.cli_utils import get_existing_id_and_project, get_kpop_or_not
from src.dw_poster import DWPoster
from src.tumblr_poster import TumblrPoster
from src.project import ProjectsTracker
from src.tweet_poster import TweetPoster


if __name__ == "__main__":
    parser = ArgumentParser(prog="Podfic project promo!", description="Use once the work is posted")
    parser.add_argument('--quiet', '-q', help="quiet mode",
        action='store_true', required=False)
    parser.add_argument('--link', help="link to the ao3 work", default=None)
    parser.add_argument('--fandom', help="abreviation of the fandom " + \
        "(like at the start of the mp3 file name)", default=None)
    parser.add_argument('--title', help="title of the work", default=None)
    parser.add_argument('--id', help="id of the project", default=None)
    args = parser.parse_args()

    verbose = not args.quiet
    tracker = ProjectsTracker(tracker_path="/home/anna/Music/tracker.json", verbose=verbose)
    id, project = get_existing_id_and_project(tracker, args.id, args.fandom, args.title, verbose)
    
    # Drafting dw post
    dw_poster = DWPoster(project, verbose)
    dw_poster.save_dw_post_text()

    # Promoting on twitter
    tweet_poster = TweetPoster(project, verbose)
    tweet_poster.post_promo(is_kpop=get_kpop_or_not())


    # Promoting on tumblr
    tumblr_poster = TumblrPoster(project, verbose)
    tumblr_poster.post_promo()

    # Promoting on Mastodon
    # TODO
