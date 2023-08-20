# -*- coding: utf-8 -*-
""" Tumblr promo poster
https://api.tumblr.com/console/calls/user/info -> Register a new app
Application name: Podfic Promo
Application Description: Automatically post cover art, description of podfic and link to ao3
Application Website: https://localhost/
Default callback URL: https://localhost/
OAuth2 redirect URLs (space separate): https://localhost/
Save OAuth Consumer Key and Consumer Secret under tumblr_consumer_key and tumblr_consumer_secret
in settings.json, add also the name of your blog under tumblr_blog_name
Click "Explore API", enter the consumer key and consumer secret,
save the last two keys of the generated code as tumblr_oauth_token and tumblr_oauth_secret """


from requests_oauthlib import OAuth1Session
from pytumblr import TumblrRestClient
from src.secret_handler import get_secrets, get_oauth1_tokens
from src.base_object import BaseObject
from src.template_filler import TumblrTemplate
from src.project import Project


class TumblrError(Exception): pass


class TumblrPoster(BaseObject):
    """ Tumblr promo poster!
    Uses the official tumblr API """

    def __init__(self, project:Project, verbose:bool=True) -> None:
        super().__init__(verbose)
        self._project_id = project.project_id
        self._files = project.files
        self._project_metadata = project.metadata
        self._client = self._get_client()
        self._template = TumblrTemplate(project, verbose)

    def _get_client(self) -> TumblrRestClient:
        """ Sets up pytumblr API client """
        # Get saved secrets
        consumer_key, consumer_secret = get_secrets(
            ["tumblr_consumer_key", "tumblr_consumer_secret"])

        # Get oauth tokens
        request_token_url = 'http://www.tumblr.com/oauth/request_token'
        authorize_url = 'http://www.tumblr.com/oauth/authorize'
        access_token_url = 'http://www.tumblr.com/oauth/access_token'
        oauth_token, oauth_token_secret = get_oauth1_tokens(consumer_key, consumer_secret, request_token_url,
            authorize_url, access_token_url)

        # oauth_session = OAuth1Session(
        #     consumer_key,
        #     client_secret=consumer_secret,
        #     resource_owner_key=resource_owner_key,
        #     resource_owner_secret=resource_owner_secret,
        #     verifier=verifier
        # )
        # oauth_tokens = oauth_session.fetch_access_token(access_token_url)

        # Get client
        return TumblrRestClient(consumer_key, consumer_secret, oauth_token, oauth_token_secret)

    def post_promo(self) -> None:
        """ Posts a promo tumblr post using cover art image, metadata info and ao3 link """
        self._vprint("\nDrafting promo tumblr post...", end=" ")
        
        # Making the request
        blog = get_secrets(["tumblr_blog_name"])[0]
        print(blog)
        response = self._client.create_text(blog, state="queue", format="html",
            title="test", body="test")
        response = self._client.create_text(blog, state="queue", tags=self._template.tags, format="html",
            title=self._template.title, body=self._template.body)
        
        # Checking results
        if "meta" in response and response['meta']['status'] == 404:
            raise TumblrError(
                "Tumblr posting failed: "+str(response)+"\nTitle: "+\
                self._template.title+"\nText: "+self._template.body)
        self._vprint("Promo tumblr post posted!")

        # print("\nIs this a kpop podfic?")
        # print("- No (hit return without typing anything)")
        # print("- Yes (type anything then hit return)")
        # choice = input("Your choice? ")
        # if choice:
        #     payload = {"text":"@kpop_podfic <3", "reply":{
        #         "in_reply_to_tweet_id":response.json()["data"]["id"]}}
        #     self._post(payload)
        #     self._vprint("kpop_podfic mentionned")
