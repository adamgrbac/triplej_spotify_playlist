"""
triplej_playlist.py

This script was originally built to make a spotify playlist from the songs
played on TripleJ during Requestival.

Generically the script uses the TripleJ API to get a list of songs played on
a particular day between 6am and 9pm, searches for them on spotify, and if items
finds them - adds them to a new playlist.

To use this script please input your own CLIENT_ID & CLIENT_SECRET from
Spotify, as well as specifying the play_date you with to generate a playlist
from and the name of the desired playlist (PLAYLIST_NAME).

The SCOPE variable can be altered if you wish, however the default settings
have been tested and will work.

Author: Adam Grbac
Date: 25/05/2021
Email: adam.grbac@gmail.com
"""

import datetime
import os
import requests
from utils import get_spotify_authtoken, generate_triplej

#########################################################
# Set variables to create playlist and login to spotify #
#########################################################

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SCOPE = "user-library-read user-read-private user-read-email \
playlist-modify-public playlist-modify-private playlist-read-private"

play_date = datetime.date(2021, 5, 23)
PLAYLIST_NAME = "SpotifyAPI Test"

##################################
# Step 1: Get spotify auth token #
##################################

# If refresh.token file exists, get contents to use for authorization
try:
    with open("refresh.token", encoding="utf-8") as f:
        REFRESH_TOKEN = f.readline()
except Exception:
    print("Refresh token unavailable!")
    REFRESH_TOKEN = None

# Use helper function to authorize application
AUTH_TOKEN, REFRESH_TOKEN = get_spotify_authtoken(CLIENT_ID,
                                                  CLIENT_SECRET,
                                                  SCOPE,
                                                  REFRESH_TOKEN)

# If a new refresh token is returned, save it to file refresh.token
if REFRESH_TOKEN:
    with open("refresh.token", "w", encoding="utf-8") as f:
        f.write(REFRESH_TOKEN)

##############################
# Step 2: Get Spotify UserID #
##############################

auth_header = {"Authorization": f"Bearer {AUTH_TOKEN}"}
res = requests.get("https://api.spotify.com/v1/me", headers=auth_header)
USERID = res.json()["id"]

###############################
# Step 3: Create new playlist #
###############################

playlist_url = f"https://api.spotify.com/v1/users/{USERID}/playlists"
playlist_data = {"name": PLAYLIST_NAME,
                 "public": True,
                 "description": "SpotifyAPI Generated Playlist"}
res = requests.post(playlist_url, headers=auth_header, json=playlist_data)
if res.status_code == 201:
    print("Playlist created!")
    PLAYLISTID = res.json()["id"]
else:
    raise Exception("Couldn't create playlist!")

##################################################################
# Step 4: Get TripleJ Playlist and add songs to Spotify Playlist #
##################################################################

for title, artist in generate_triplej(play_date):
    # Search for track on spotify by title and artist.
    query = f"{title} artist:{artist}"
    res = requests.get(f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1",
                       headers=auth_header)

    # If song cannot be found, skip.
    try:
        uri = res.json()["tracks"]["items"][0]["uri"]
    except Exception:
        print(f"Couldn't find spotify track: {title} by {artist}")
        continue

    # POST song uri to playlist to add it.
    res = requests.post(f"https://api.spotify.com/v1/playlists/{PLAYLISTID}/tracks",
                        headers=auth_header,
                        json={"uris": [uri]})
    if res.status_code != 201:
        print(res)
        print(f"Error adding track {title} by {artist}")
