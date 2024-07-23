from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

date = input("Which year do you want to travel to? "
             "Type the date in this format YYYY-MM-DD: ")
year = date.split("-")[0]

SPOTIFY_REDIRECT_URI = os.environ["DB_SPOTIFY_REDIRECT_URI"]
SPOTIFY_CLIENT_ID = os.environ["DB_SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["DB_SPOTIFY_CLIENT_SECRET"]
SPOTIFY_PLAYLIST_NAME = "Top 100 songs"
SPOTIFY_USER_ID= "Saumil Upadhyay"
SPOTIFY_PLAYLIST_DESCRIPTION = f"Provides Top 100 Songs from {year}"

URL = f"https://www.billboard.com/charts/hot-100/{date}/"
response = requests.get(URL)

soup = BeautifulSoup(response.text, "html.parser")
all_songs = soup.select("li ul li h3")
song_names = [songs.getText().strip() for songs in all_songs]
print(song_names)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=SPOTIFY_REDIRECT_URI,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
        username=SPOTIFY_USER_ID,
    )
)
user_id = sp.current_user()["id"]
print(user_id)

song_uris = []
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(
    user=user_id,
    name=SPOTIFY_PLAYLIST_NAME,
    public=False,
    description=SPOTIFY_PLAYLIST_DESCRIPTION
)
print(f"Created playlist: {playlist['name']} with ID: {playlist['id']}")

sp.playlist_add_items(playlist_id=playlist['id'], items=song_uris)
print("Tracks added to the playlist successfully.")