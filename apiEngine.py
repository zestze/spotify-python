import sys
import requests
import requests.auth
import string
import re
import flask
import datetime
import json

class ApiEngine:
    def __init__(self):
        # needed for the client program as a whole to work.
        clientID = ""
        clientSecret = ""
        clientIdAndSecretBase64 = ""
        # granted per user, and might change
        REFRESH_TOKEN = ""
        ACCESS_TOKEN = ""
        TOKEN_TYPE = ""
        # per user info
        # @TODO: decide if going to carry this info around.
        # userID = "" ...

    def moveDiscoverSongsToPlaylist(self, userID, discoverID, madePlaylistJson, tracksJson):
        uri = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(
            userID, madePlaylistJson["id"])
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN),
                   "Content-Type": "application/json"}
        uris = []
        for item in tracksJson["items"]:
            track = item["track"]
            u = track["uri"]
            uris.append(u)
        data = json.dumps({"uris": uris})
        response = requests.post(uri, headers=headers, data=data)

    def doesPlaylistExistAlready(self, playlistName, userID):
        """ """
        uri = "https://api.spotify.com/v1/users/{}/playlists".format(userID)
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN)}
        payload = {"limit": "50"}
        response = requests.get(uri, headers=headers, params=payload)
        rJson = response.json()

        for item in rJson["items"]:
            if item["name"] == playlistName:
                return True
        return False

    def makePlaylist(self, userID):
        """@TODO: check if playylist already exists"""

        uri = "https://api.spotify.com/v1/users/{}/playlists".format(userID)
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN),
                   "Content-Type": "application/json"}
        playlistName = "Discovered on {}".format(datetime.date.today())

        alreadyExists = self.doesPlaylistExistAlready(playlistName, userID)
        if alreadyExists:
            return None

        data = json.dumps({"name": playlistName, "public": "false"})

        response = requests.post(uri, headers=headers, data=data)

        return response.json()

    def grabCredentials(self):
        with open('client.id', 'r') as myFile:
            self.clientID = myFile.read().replace('\n', '')
        with open('client.id_secret.64', 'r') as myFile:
            self.clientIdAndSecretBase64 = myFile.read().replace('\n', '')
        with open('client.secret', 'r') as myFile:
            self.clientSecret = myFile.read().replace('\n', '')

    def refreshToken(self):
        data = {"grant_type": "refresh_token", "refresh_token": self.REFRESH_TOKEN}
        headers = {"Authorization": "Basic {}".format(self.clientIdAndSecretBase64)}
        response = requests.post("https://accounts.spotify.com/api/token",
                                 data=data, headers=headers)
        rJson = response.json()
        accessToken = rJson['access_token']
        tokenType = rJson['token_type']
        # also have 'scope' and 'expires_in' keys
        return accessToken

    def getDiscoverID(self):
        """
        @TODO: need to pass a 'limit' of 50.
                also store the name of the first playlist.
                so if run into name of first playlist again, gone in a circle, and leave.
        """
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN)}
        query_params = {"limit": "50"}
        response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers,
                               params=query_params)
        rJson = response.json()

        playlistsList = rJson['items'] # is a list of dictionaries
        first = True
        firstID = ""
        for pJson in playlistsList:
            if first:
                firstID = pJson['id']
            if pJson['name'] == 'Discover Weekly':
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

    def getUserID(self):
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN)}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        rJson = response.json()
        return rJson['id']

    def getDiscoverTracks(self, userID, discoverID):
        headers = {"Authorization": "{} {}".format(self.TOKEN_TYPE, self.ACCESS_TOKEN)}
        userID = "spotify" # this is only overwritten because discover playlists are weird
        response = requests.get("https://api.spotify.com/v1/users/{}/playlists/{}/tracks" \
                                .format(userID, discoverID), headers=headers)
        #print (response.url)
        rJson = response.json()
        return rJson
