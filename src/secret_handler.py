# -*- coding: utf-8 -*-
""" Secret handler
For passwords, tokens, and keys in settings.json """


from json import load as js_load, dump as js_dump
from typing import Dict, List, Tuple, Union
from requests_oauthlib import OAuth1Session


class LoginError(Exception): pass

def get_secrets(keys:List[str], ) -> List[str]:
    """ Fetches secrets from saved info """
    with open("settings.json", "r") as file:
        settings = js_load(file)
    for k in keys:
        if not k in settings: raise ValueError(f"Missing {k} in settings.json")
    return [settings[k] for k in keys]


def request_new_secrets(keys:List[str]) -> None:
    """ Requests new secrets from the user, saves them """
    # Use the CLI interface to ask the user for input
    with open("settings.json", "r") as file:
        settings = js_load(file)
        for k in keys:
            settings[k] = input(f"{k}? ")
    # Save the credentials and try again
    with open("settings.json", 'w') as file:
        js_dump(settings, file)


def set_secrets(new_secrets:Dict[str,str]) -> None:
    """ Saves the given secrets in memory """
    # Load existing secrets and update them
    with open("settings.json", "r") as file:
        settings = js_load(file)
        for k, v in new_secrets.items():
            settings[k] = v
    # Save the credentials
    with open("settings.json", 'w') as file:
        js_dump(settings, file)


def request_url_authorization(url:str) -> str:
    """ Asks the user to click on the link and input the redirected URL or given PIN """
    # TODO put that in the CLI
    print("\nPlease go here and authorize: %s" % url)
    return input("Paste the PIN or full URL here: ")


def get_oauth1_tokens(consumer_key:str, consumer_secret:str,
    request_token_url:str, authorize_url:str, access_token_url:str,
    pin:bool=False) -> Union[Tuple[str, str], Tuple[str,str,str]]:
    """ Fetches a new oauth token and oauth secret
    Based on https://github.com/tumblr/pytumblr/blob/master/interactive_console.py """
    # Obtain request token
    oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
    try:
        fetch_response = oauth_session.fetch_request_token(request_token_url)
    except ValueError:
        raise LoginError("There may have been an issue with the consumer key or " +\
            "consumer secret you entered.")

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # Authorize URL + Response
    full_authorize_url = oauth_session.authorization_url(authorize_url)

    # Redirect to authentication page
    redirect_response = request_url_authorization(full_authorize_url)

    # Retrieve oauth verifier
    if pin:
        verifier = redirect_response
    else:
        oauth_response = oauth_session.parse_authorization_response(redirect_response)
        verifier = oauth_response.get('oauth_verifier')

    # Request final access token
    oauth_session = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )
    oauth_tokens = oauth_session.fetch_access_token(access_token_url)

    # Return token and token secret
    return oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')

