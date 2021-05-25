"""
utils.py

This file provides a couple of helper functions to build the TripleJ Spotify
playlist.

Author: Adam Grbac
Date: 25/05/2021
Email: adam.grbac@gmail.com
"""

import datetime
import base64
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


def get_spotify_authtoken(client_id, client_secret, scope, refresh_token=None,
                          redirect_uri="https://example.com/callback"):
    """
    get_spotify_authtoken(client_id, client_secret, scope, refresh_token,
                          redirect_uri) -> (auth_token, refresh_token)

    This function connects to the Spotify Auth API and performs the OAuth
    mechanism to allow user login.

    Arguments:
    client_id - Client ID provided by Spotify API
    client_secret - Client Secret provided by Spotify API
    scope - Scope of the application. Used to control access for the user
    refresh_token - (Optional) The refresh token to be used to generate_triplej
                    a new auth token.
    redirect_uri - (Optional) The uri to redirect to during the OAuth
                   procedure

    Returns:
    auth_token - The authorization token provided by the spotify API to
                 authenticate requests going forward
    refresh_token - (Optional) The new refresh token provided by the
                    spotify API (if supplied)
    """

    # If refresh token has been passed in, try to use it to generate a
    # new auth_token.

    if refresh_token:
        # Setup Base64 Client Secret to Send
        secret = f"{client_id}:{client_secret}"
        b64_secret = base64.b64encode(bytes(secret, "utf-8")).decode("utf-8")

        body = {"grant_type": "refresh_token",
                "refresh_token": refresh_token}
        auth_url = "https://accounts.spotify.com/api/token"
        auth_header = {"Authorization": f"Basic {b64_secret}"}

        res = requests.post(auth_url, data=body, headers=auth_header)

        auth_token = res.json()["access_token"]
        try:
            refresh_token = res.json()["refresh_token"]
        except Exception:
            refresh_token = None

    # If no refresh token is available, generate a new auth_token by
    # prompting the user to login and authorise the application.

    else:
        auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"

        # Setup Browser
        opts = Options()
        opts.add_argument('--no-sandbox')
        browser = Chrome("./chromedriver/chromedriver", options=opts)

        # Go to auth page, sign-in and wait for code to be returned
        browser.get(auth_url)
        WebDriverWait(browser, 60).until(EC.url_contains(redirect_uri))

        # Pull auth code from redirect_uri & close browser
        code = browser.current_url.split("code=")[1].split("#")[0]
        browser.close()

        # Step 2: Auth Token

        body = {"grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret}
        auth_url = "https://accounts.spotify.com/api/token"
        res = requests.post(auth_url, data=body)
        auth_token = res.json()["access_token"]
        try:
            refresh_token = res.json()["refresh_token"]
        except Exception:
            refresh_token = None

    return (auth_token, refresh_token)


def generate_triplej(play_date, batch_size=100):
    """
    generate_triplej(play_date, batch_size) -> generator((title, artist))

    This generator function yields successive songs from the triplej playlist
    on the date "play_date".

    Arguments:
    play_date - This is used to select the date the songs were played on
                TripleJ
    batch_size - This argument controls the internal batching between the
                 script and the TripleJ API. It is capped at 100.

    Yields:
    (title, artist) - This generator yields pairs of titles and artists
                      which can be used to search on spotify
    """

    # Check batch_size parameter is between 1 - 100
    if batch_size > 100:
        print("Batch size limited to 100 due to API restrictions")
        batch_size = 100
    elif batch_size < 1:
        print("Batch size must be 1 or greater, reverting to 1")
        batch_size = 1

    # Convert play_date to appropriate strings for query
    play_date_1 = play_date - datetime.timedelta(days=1)
    play_date_str = play_date.strftime('%Y-%m-%d')
    play_date_1_str = play_date_1.strftime('%Y-%m-%d')

    offset = 0
    has_songs = True

    # Get songs from TripleJ API in batches until empty
    while has_songs:
        triplej_url = f"https://music.abcradio.net.au/api/v1/plays/search.json?station=triplej&from={play_date_1_str}T20:00:00&to={play_date_str}T10:59:59&limit={batch_size}&offset={offset}&order=desc"
        res = requests.get(triplej_url)
        len_list = len(res.json()["items"])
        if len_list == 0:
            has_songs = False
        for item in res.json()["items"]:
            title = item["recording"]["title"]
            artist = item["recording"]["artists"][0]["name"]
            yield (title, artist)
        offset += batch_size
