# -*- coding: utf-8 -*-
""" Promo tweet poster
Code copied and adapted from https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py#L11
For a description of the API, see https://api.twitter.com/2/openapi.json

To set up, follow this guide: https://developer.twitter.com/en/docs/tutorials/tweeting-media-v2
Set up permission for read, write and message
You'll also need to save your app's API information in settings.json:
- twitter_api_key
- twitter_api_secret
For more information, see
- https://stackoverflow.com/questions/70891698/how-to-post-a-tweet-with-media-picture-using-twitter-api-v2-and-tweepy-python
- https://stackoverflow.com/questions/66156958/how-to-acess-tweets-with-bearer-token-using-tweepy-in-python

"""

from tweepy import OAuth1UserHandler, API
from requests_oauthlib import OAuth1Session
from typing import Dict
from json import load as js_load
from requests.models import Response
from src.base_object import VerboseObject
from src.template_filler import TwitterTemplate


class TweetPoster(VerboseObject):
    """ Twitter promo poster!
    Uses the official twitter APIs """

    def __init__(self, project_id, files, metadata, verbose=True):
        super().__init__(verbose)
        self._project_id = project_id
        self._files = files
        self._project_metadata = metadata
        # Option not to promo for unrevealed works, ex: challenges
        print("\nDo you want to promo this work now?")
        print("- Yes (hit return without typing anything)")
        print("- No (type anything then hit return)")
        choice = input("Your choice? ")
        if choice:
            self._skip_promo = True
            return
        else:
            self._get_secrets()
            self._get_sessions()
            self._template = TwitterTemplate(metadata, verbose)

    def _get_secrets(self) -> None:
        """ Fetches API key and secret """
        with open("settings.json", "r") as file:
            settings = js_load(file)
        for k in ["twitter_api_key", "twitter_api_secret"]:
            # "twitter_access_token", "twitter_access_token_secret", "twitter_client_id",
            # "twitter_client_secret"]:
            assert k in settings, f"Missing {k} in settings.json"
        self._consumer_key = settings["twitter_api_key"]
        self._consumer_secret = settings["twitter_api_secret"]

    def _get_sessions(self) -> None:
        """ Set up tweet and media sessions """
        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(self._consumer_key, client_secret=self._consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            assert False, "There may have been an issue with the twitter consumer_key or " +\
                "consumer_secret you entered."

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("\nPlease go here and authorize: %s" % authorization_url)
        verifier = input("Paste the PIN here: ")

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            self._consumer_key,
            client_secret=self._consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )

        oauth_tokens = oauth.fetch_access_token(access_token_url)
        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        oauth = OAuth1Session(
            self._consumer_key,
            client_secret=self._consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        self._post_session = oauth

        # Media upload is done with tweepy
        cover_auth = OAuth1UserHandler(self._consumer_key, self._consumer_secret)
        cover_auth.set_access_token(access_token, access_token_secret)
        self._cover_session = API(cover_auth)
            
    
    def tweet_promo(self) -> None:
        """ Posts a promo tweet using cover art image and ao3 link """
        if self._skip_promo:
            self._vprint("No promo yet, skipping")
            return
        
        self._vprint("Drafting promo tweet...", end=" ")
        # Cover art
        cover_paths = self._files.cover.compressed
        cover_ids = []
        for c in cover_paths:
            cover = self._cover_session.media_upload(filename=c)
            cover_ids.append(cover.media_id_string)

        # Making the request
        response = self._tweet({"text": self._template.tweet, "media":{"media_ids":cover_ids}})
        self._vprint("Promo tweet posted!")
        print("\nIs this a kpop podfic?")
        print("- No (hit return without typing anything)")
        print("- Yes (type anything then hit return)")
        choice = input("Your choice? ")
        if choice:
            payload = {"text":"@kpop_podfic <3", "reply":{
                "in_reply_to_tweet_id":response.json()["data"]["id"]}}
            self._tweet(payload)
            self._vprint("kpop_podfic mentionned")


    def _tweet(self, payload:Dict) -> Response:
        """ Tweet the given data """
        response = self._post_session.post("https://api.twitter.com/2/tweets", json=payload)
        assert response.status_code == 201, \
                "Request returned an error: {} {} for {}".format(
                    response.status_code, response.text, payload)
        return response
