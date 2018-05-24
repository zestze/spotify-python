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

app = flask.Flask(__name__)

_USER_AGENT_ = "simpleSpotifyClient/0.1 by Zeke"

# needs to be space separated
SCOPES = "playlist-read-private user-top-read user-read-recently-played" \
        " user-library-read user-read-private"
PORT = 8888
REDIRECT_URI = "http://127.0.0.1:8888/callback"

client_id = ""
client_secret = ""
client_is_base64 = ""

REFRESH_TOKEN = ""
ACCESS_TOKEN = ""
TOKEN_TYPE = ""

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
    headers = {"Authorization": "{} {}".format(TOKEN_TYPE, ACCESS_TOKEN)}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    rJson = response.json()

    playlistsList = rJson['items'] # is a list of dictionaries
    for pJson in playlistsList:
        if pJson['name'] == 'Discover Weekly':
            print (pJson)
            return pJson['id']

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

    return str(tracksJson)

if __name__ == "__main__":
    print ("Starting spotify client")
    app.run(port=PORT)
