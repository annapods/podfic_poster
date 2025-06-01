# -*- coding: utf-8 -*-
""" Promo tweet poster
Code copied and adapted from https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py#L11
For a description of the API, see https://api.twitter.com/2/openapi.json

For more information, see
- https://stackoverflow.com/questions/70891698/how-to-post-a-tweet-with-media-picture-using-twitter-api-v2-and-tweepy-python
- https://stackoverflow.com/questions/66156958/how-to-acess-tweets-with-bearer-token-using-tweepy-in-python
"""

from tweepy import OAuth1UserHandler, API
from requests_oauthlib import OAuth1Session
from typing import Dict
from json import load as js_load
from requests.models import Response
from src.base_object import BaseObject
from src.template_filler import TwitterTemplate
from src.secret_handler import get_secrets, get_oauth1_tokens, set_secrets
from src.project import Project


class TwitterError(Exception): pass


class TweetPoster(BaseObject):
    """ Twitter promo poster!
    Uses the official twitter APIs """

    def __init__(self, project:Project, verbose:bool=True) -> None:
        super().__init__(verbose)
        self._project_id = project.project_id
        self._files = project.files
        self._project_metadata = project.metadata
        self._get_clients()
        self._template = TwitterTemplate(project, verbose)
        try: self._last_promo_tweet = get_secrets(["twitter_last_promo"])[0]
        except ValueError: self._last_promo_tweet = None

    def _get_clients(self) -> None:
        """ Set up tweet and media clients """
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        authorize_url = "https://api.twitter.com/oauth/authorize"
        access_token_url = "https://api.twitter.com/oauth/access_token"

        # Get secrets
        consumer_key, consumer_secret = get_secrets(["twitter_api_key", "twitter_api_secret"])
        access_token, access_token_secret = get_oauth1_tokens(consumer_key, consumer_secret,
            request_token_url, authorize_url, access_token_url, pin=True)

        # Tweet client
        self._post_session = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        # Media upload tweepy client
        cover_auth = OAuth1UserHandler(consumer_key, consumer_secret)
        cover_auth.set_access_token(access_token, access_token_secret)
        self._cover_session = API(cover_auth)
            
    def post_promo(self, is_kpop:bool=False) -> None:
        """ Posts a promo tweet using cover art image and ao3 link """
        self._vprint("Drafting promo tweet...", end=" ")
        
        # Cover art
        cover_paths = self._files.cover.compressed
        cover_ids = []
        for c in cover_paths:
            cover = self._cover_session.media_upload(filename=c)
            cover_ids.append(cover.media_id_string)

        # Promo tweet
        payload = {"text": self._template.tweet, "media":{"media_ids":cover_ids}}
        if self._last_promo_tweet: payload["reply"] = {'in_reply_to_tweet_id': self._last_promo_tweet}
        response = self._post(payload)
        self._vprint("Promo tweet posted!")
        # Saving new tweet as last promo tweet
        self._last_promo_tweet = response.json()["data"]["id"]
        set_secrets({"twitter_last_promo": self._last_promo_tweet})
        # @ promo account
        if is_kpop:
            payload = {"text":"@kpop_podfic <3", "reply":{
                "in_reply_to_tweet_id":self._last_promo_tweet}}
            self._post(payload)
            self._vprint("Kpop podfic account mentioned!")

    def _post(self, payload:Dict) -> Response:
        """ Tweet the given data """
        response = self._post_session.post("https://api.twitter.com/2/tweets", json=payload)
        if not response.status_code == 201:
            raise TwitterError("Request returned an error: {} {} for {}".format(
                    response.status_code, response.text, payload))
        return response
