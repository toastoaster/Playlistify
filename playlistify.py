# access metadata mp3
# with exif
# with eyeD3

# entfernen: lyrics, official video, nicht-alphabet zeichen, hq

import creds
import requests
import random
from urllib.parse import urlencode
import os
import re

FILE_TYPES = ["m4a", "M4A", "mp3", "MP3", "wav", "WAV"]
playlist_id = ""
songnames = []

def create_playlist():
  playlist_name = "CGEN#" + \
      str(random.randint(100_000_000_000, 999_999_999_999))
  body = {
      "name": playlist_name,
      "description": "Playlist computer-generated from a bunch of old files.",
      "public": "false"
  }
  res = requests.post(
      "https://api.spotify.com/v1/users/" + creds.user + "/playlists",
      headers={
          "Accept": "application/json",
          "Content-Type": "application/json",
          "Authorization": "Bearer " + creds.token
      },
      json=body
  )
  if res.status_code == 201:
    print("Playlist named " + playlist_name + " created.")
    global playlist_id
    playlist_id = res.json()["id"]
  else:
    print("Playlist not created: " + str(res.status_code))
    return


def add_songs():
  songids = []
  for song_name in songnames:
    print(re.sub('lyrics|official video|hq', '', song_name, flags=re.IGNORECASE))
    query = {
        "q": re.sub('lyrics|official video|hq', '', song_name, flags=re.IGNORECASE),
        "type": "track",
        "limit": 1,
        "offset": 0
    }
    res = requests.get(
        "https://api.spotify.com/v1/search?" + urlencode(query),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + creds.token
        }
    )
    if res.status_code == 200 and len(res.json()["tracks"]["items"]) > 0:
      print(song_name + " found as " + res.json()["tracks"]["items"][0]["name"] + ".")
      songids.append("spotify:track:" + res.json()["tracks"]["items"][0]["id"])
    else:
      print(song_name + " not found: " + str(res.status_code))

  playlist_endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
  uris = []
  i = 0
  for id in songids:
    uris.append(id)
    i = i+1
    if i%100 == 0:
      send_songs(playlist_endpoint=playlist_endpoint, uris=uris)
      uris = []
  send_songs(playlist_endpoint=playlist_endpoint, uris=uris)

def send_songs(playlist_endpoint, uris):
  res = requests.post(
      playlist_endpoint,
      headers={
          "Accept": "application/json",
          "Content-Type": "application/json",
          "Authorization": "Bearer " + creds.token
      },
      json={"uris": uris}
  )
  if res.status_code == 201:
    print("Adding songs.")
  else:
    print("Some songs not added: " + str(res.status_code))
    return

def get_songnames():
  path = os.getcwd()
  # Get proper files in directory
  files = [f for f in os.listdir(
      path) if os.path.isfile(os.path.join(path, f))]
  global songnames
  # Check if soundfile and cut off suffix
  for f in files:
    f_split = f.split(".")
    if f_split[-1] in FILE_TYPES:
      songnames.append("".join(f_split[:-1]))


if __name__ == "__main__":
  if playlist_id == "":
    create_playlist()
  if playlist_id != "":
    get_songnames()
    add_songs()
    print("Finish!")
