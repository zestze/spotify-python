#!/usr/bin/env python3
"""
@TODO: refresh token function

@TODO: change global stuff, wrap in a class
"""
import sys
import requests
import requests.auth
import string
import re
import flask
import datetime
import json

app = flask.Flask(__name__)

_USER_AGENT_ = "simpleSpotifyClient/0.1 by Zeke"

# needs to be space separated
SCOPES = "playlist-read-private user-top-read user-read-recently-played" \
        " user-library-read user-read-private playlist-modify-private"
PORT = 8888
REDIRECT_URI = "http://127.0.0.1:8888/callback"

client_id = ""
client_secret = ""
client_is_base64 = ""

REFRESH_TOKEN = ""
ACCESS_TOKEN = ""
TOKEN_TYPE = ""

def moveDiscoverSongsToPlaylist(userID, discoverID, madePlaylistJson, tracksJson):
    """ POST https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks """

    uri = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(
        userID, madePlaylistJson["id"])
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN),
               "Content-Type": "application/json"}

    uris = []
    #print (tracksJson)
    for item in tracksJson["items"]:
        track = item["track"]
        u = track["uri"]
        uris.append(u)

    # might have to put uris in str()
    data = json.dumps({"uris": uris})

    response = requests.post(uri, headers=headers, data=data)

def doesPlaylistExistAlready(playlistName, userID):
    """ """
    uri = "https://api.spotify.com/v1/users/{}/playlists".format(userID)
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN)}
    payload = {"limit": "50"}
    response = requests.get(uri, headers=headers, params=payload)
    rJson = response.json()

    for item in rJson["items"]:
        if item["name"] == playlistName:
            return True
    return False


def makePlaylist(userID):
    """@TODO: check if playylist already exists"""

    uri = "https://api.spotify.com/v1/users/{}/playlists".format(userID)
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN),
               "Content-Type": "application/json"}
    playlistName = "Discovered on {}".format(datetime.date.today())

    alreadyExists = doesPlaylistExistAlready(playlistName, userID)
    if alreadyExists:
        return None

    data = json.dumps({"name": playlistName, "public": "false"})

    response = requests.post(uri, headers=headers, data=data)

    return response.json()

def grabCredentials():
    global client_id
    global client_is_base64
    global client_secret
    with open('client.id', 'r') as myFile:
        client_id = myFile.read().replace('\n', '')
    with open('client.id_secret.64', 'r') as myFile:
        client_is_base64 = myFile.read().replace('\n', '')
    with open('client.secret', 'r') as myFile:
        client_secret = myFile.read().replace('\n', '')

def refreshToken():
    data = {"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN}
    headers = {"Authorization": "Basic {}".format(client_is_base64)}
    response = requests.post("https://accounts.spotify.com/api/token",
                             data=data, headers=headers)
    rJson = response.json()
    accessToken = rJson['access_token']
    tokenType = rJson['token_type']
    # also have 'scope' and 'expires_in' keys
    return accessToken

@app.route('/')
def home():
    grabCredentials()

    headers = {"User-Agent": _USER_AGENT_}
    query_params = {"client_id": client_id, "response_type": "code", "redirect_uri": \
                    REDIRECT_URI, "scope": SCOPES}

    response = requests.get("https://accounts.spotify.com/authorize",
                            headers=headers,
                            params=query_params)

    return flask.redirect(response.url)

def getDiscoverID():
    """
    @TODO: need to pass a 'limit' of 50.
            also store the name of the first playlist.
            so if run into name of first playlist again, gone in a circle, and leave.
    """
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN)}
    query_params = {"limit": "50"}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers,
                           params=query_params)
    rJson = response.json()

    #print ("rjson: {}".format(rJson))
    playlistsList = rJson['items'] # is a list of dictionaries
    #print ("palylistsList: {}".format(playlistsList))
    first = True
    firstID = ""
    for pJson in playlistsList:
        if first:
            firstID = pJson['id']
        #print ("pJson['name'] == {}".format(pJson['name']))
        if pJson['name'] == 'Discover Weekly':
            #print (pJson)
            return pJson['id']

    seenAll = False
    while not seenAll:
        response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers,
                               params=query_params)
        rJson = response.json()
        playlistsList = rJson['items']
        for pJson in playlistsList:
            if pJson['id'] == firstID:
                seenAll = True
                break
            if pJson['name'] == 'Discover Weekly':
                return pjson['id']

    raise Exception("Discover Weekly Playlist not found")

def getUserID():
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN)}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    rJson = response.json()
    return rJson['id']

def getDiscoverTracks(userID, discoverID):
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN)}
    userID = "spotify" # this is only overwritten because discover playlists are weird
    response = requests.get("https://api.spotify.com/v1/users/{}/playlists/{}/tracks" \
                            .format(userID, discoverID), headers=headers)
    #print (response.url)
    rJson = response.json()
    return rJson

@app.route('/callback')
def callback():
    authToken = flask.request.args['code']
    # should also check for 'error' or 'state'

    data = {"grant_type": "authorization_code", "redirect_uri": REDIRECT_URI,
            "code": str(authToken), "client_id": client_id,
            "client_secret": client_secret}
    response = requests.post("https://accounts.spotify.com/api/token",
                             data=data)
    rJson = response.json()
    #print (rJson)
    tokenType = rJson['token_type']
    global TOKEN_TYPE
    TOKEN_TYPE = tokenType
    accessToken = rJson['access_token']
    global ACCESS_TOKEN
    ACCESS_TOKEN = accessToken
    refreshToken = rJson['refresh_token']
    global REFRESH_TOKEN
    REFRESH_TOKEN = refreshToken

    # need to get playlist id for discover playlist
    # then user id
    # then do something with the track data points

    discoverID = getDiscoverID()
    print (discoverID)
    userID = getUserID()
    print (userID)
    tracksJson = getDiscoverTracks(userID, discoverID)

    madePlaylistJson = makePlaylist(userID)
    if madePlaylistJson:
        moveDiscoverSongsToPlaylist(userID, discoverID, madePlaylistJson, tracksJson)

    #return str(tracksJson)
    return "Successfully recorded Discover Playlist songs"

if __name__ == "__main__":
    print ("Starting spotify client")
    app.run(port=PORT)
