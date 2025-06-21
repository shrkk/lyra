import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

scope = (
    "user-top-read "
    "user-read-recently-played "
    "user-read-currently-playing "
    "user-read-playback-state "
    "user-modify-playback-state "
    "playlist-read-private "
    "playlist-modify-private "
    "playlist-modify-public "
    "user-library-read "
    "user-library-modify "
    "user-follow-read "
    "user-follow-modify "
    "user-read-private"
)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope
))
