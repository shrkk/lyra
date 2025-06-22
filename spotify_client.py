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

# The global 'sp' instance is removed to allow for per-request authentication.
