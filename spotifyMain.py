#!/usr/bin/env python3
"""
@TODO: refresh token function
"""
import requests
import requests.auth
import string
import re
import flask
import json

from apiEngine import ApiEngine

### hard coded constants ###
USER_AGENT   = "simpleSpotifyClient/0.1 by Zeke"
SCOPES       = "playlist-read-private user-top-read user-read-recently-played " \
               "user-library-read user-read-private playlist-modify-private"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
PORT         = 8888
### hard coded constants ###

### mutable globals ###
app       = flask.Flask(__name__)
apiEngine = ApiEngine()
### mutable globals

@app.route('/')
def home():
    apiEngine.grabCredentials()

    headers = {"User-Agent": USER_AGENT}
    query_params = {"client_id": apiEngine.clientID, "response_type": "code", "redirect_uri": \
                    REDIRECT_URI, "scope": SCOPES}

    response = requests.get("https://accounts.spotify.com/authorize",
                            headers=headers,
                            params=query_params)

    return flask.redirect(response.url)

@app.route('/callback')
def callback():
    authToken = flask.request.args['code']
    # should also check for 'error' or 'state'

    data = {"grant_type": "authorization_code", "redirect_uri": REDIRECT_URI,
            "code": str(authToken), "client_id": apiEngine.clientID,
            "client_secret": apiEngine.clientSecret}
    response = requests.post("https://accounts.spotify.com/api/token",
                             data=data)
    rJson = response.json()
    apiEngine.TOKEN_TYPE    = rJson['token_type']
    apiEngine.ACCESS_TOKEN  = rJson['access_token']
    apiEngine.REFRESH_TOKEN = rJson['refresh_token']

    # need to get playlist id for discover playlist
    # then user id
    # then do something with the track data points

    discoverID = apiEngine.getDiscoverID()
    #print (discoverID)
    userID = apiEngine.getUserID()
    #print (userID)
    tracksJson = apiEngine.getDiscoverTracks(userID, discoverID)

    madePlaylistJson = apiEngine.makePlaylist(userID)
    if madePlaylistJson:
        apiEngine.moveDiscoverSongsToPlaylist(userID, discoverID, madePlaylistJson, tracksJson)

    #return str(tracksJson)
    #return "Successfully recorded Discover Playlist songs"
    return flask.render_template('success.html')

if __name__ == "__main__":
    print ("Starting spotify client")
    app.run(port=PORT)
