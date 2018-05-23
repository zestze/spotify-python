#!/usr/bin/env python3
"""
"""
import sys
import requests
import requests.auth
import string
import re

_USER_AGENT_ = "simpleSpotifyClient/0.1 by Zeke"

def grabCredentials():
    cI = ""
    cISbase64 = ""
    with open('client.id', 'r') as myFile:
        cI = myFile.read().replace('\n', '')
    with open('client.id_secret.64', 'r') as myFile:
        cISbase64 = myFile.read().replace('\n', '')
    return cI, cISbase64

def spMain(arg):
    cI, cISbase64 = grabCredentials()
    print (cI)

    headers = {"User-Agent": _USER_AGENT_}
    get_data = {"client_id": cI, "response_type": "code", "redirect_uri": \
                "http://127.0.0.1:8888/callback/"}

    response = requests.get("https://accounts.spotify.com/authorize",
                            headers=headers,
                            params=get_data)
    print (response.url)
    print (response)
    #print (response.json())
    print (response.text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("Usage: ./sp-main.py <arg1>")
    else:
        print ("Starting spotify client")
        spMain(sys.argv[1])
