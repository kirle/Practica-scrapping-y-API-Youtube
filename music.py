
"""Python script to get all titles and years of a certain artist from wikipedia
and add them chronologically on a Youtube playlist.

You will need to import your Youtube API secret key setting client_secrets_file variable to the corresponding path
"""

from typing import Optional
import wikipedia  # alternative implementation
import requests
import re
import os
from bs4 import BeautifulSoup

from googleapiclient.discovery import build

import google_auth_oauthlib.flow
import logging

# -----------------------------------------


def searchWith_wikipedia_lib(name):
	result = wikipedia.search(name)
	page = wikipedia.page(result[0])

	categories = page.categories
	content = page.content

	logging.info(content)
# -----------------------------------------


def parse_ul(uls):
	songs = []
	for child in uls:
		disc_name = child.find("i", recursive=False).text
		pattern = re.search("[1,2]{1}[0-9]{3}", child.text)
		year = pattern.group(0)
		songs.append((disc_name, year))

	return songs


def searchDiscography():
	works = []
	soup = BeautifulSoup(response.text, 'html.parser')
	wiki_text = soup.find('div', id='mw-content-text').div
	disc = wiki_text.find('span', {'id': 'Discografía'}, recursive=True)
	while not str(disc).startswith('<h2>'):
		if str(disc).startswith('<ul>'):
			disc_children = disc.findAll("li", recursive=True)
			# logging.info(disc_children)
			works += parse_ul(disc_children)
		disc = disc.next

	return works


# -----------------------------------------

def add_video_to_playlist(youtube, videoID, playlistID):
    add_video_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            'snippet': {
                'playlistId': playlistID,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': videoID
                }
                # 'position': 0
            }
        }
    ).execute()

# -----------------------------------------


def do_search(filter: str, max: int) -> Optional[str]:
	request = youtube.search().list(
            q=filter[0] + " Amaral",
            part="snippet",
            maxResults=max
        )
	response = request.execute()
	# videos = []
	# for response in response.get("items", []):
	#     if response["id"]["kind"] == "youtube#video":
	#         videos.append(response["id"]["videoId"])

	items = response.get("items", [])
	try:
		return next(v["id"]["videoId"] for v in items if v["id"]["kind"] == "youtube#video")
	except StopIteration:
		return None

# -----------------------------------------

# Youtube connection

api_key = '' #api key 
client_id = "" 
client_secrets_file= "" #path to client_secret.json file
api_service_name = 'youtube'
api_version = 'v3'

scopes = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtubepartner",
          "https://www.googleapis.com/auth/youtubepartner-channel-audit"]

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	client_secrets_file, scopes)
credentials=flow.run_console()

youtube=build(
        api_service_name, api_version, credentials = credentials)  # getting service

# Getting info from wikipedia
response=requests.get(url = "https://es.wikipedia.org/wiki/Amaral")

if(response.status_code != 200):
	logging.error("Status !200")
	exit

works=searchDiscography()
logging.debug(works)  # just for testing

# Creating playlist on YouTube
playlists_insert_response=youtube.playlists().insert(
  part="snippet,status",
  body= {
    "snippet": {
      "title": "Test Playlist",
      "description": "A private playlist created with the YouTube API v3"
    },
    "status": {
      "privacyStatus": "private"
    }
  }
).execute()

logging.info("New playlist id: %s" % playlists_insert_response["id"])
logging.info(f"New playlist id: {playlists_insert_response['id']}")

playlistID = playlists_insert_response["id"]
for work in works:
	logging.info("searching..." + str(work))
	videoId = do_search(work, 1)
	if videoId is not None:
		add_video_to_playlist(youtube, videoId, playlistID)
		logging.info("Video added \n")

logging.info("all videos added")

logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
	pass
# Fin del archivo
