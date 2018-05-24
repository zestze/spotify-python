#!/usr/bin/env python3
"""
@TODO: integrate flask support, so user can say "yes" to giving their info?
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
    tokenType = rJson['token_type']
    accessToken = rJson['access_token']
    refreshToken = rJson['refresh_token']

    headers = {"Authorization": "{} {}".format(tokenType, accessToken)}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    print (response.json())

if __name__ == "__main__":
    print ("Starting spotify client")
    app.run(debug=True, port=PORT)
