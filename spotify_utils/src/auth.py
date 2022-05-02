# Built-in modules

# PyPi modules
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_utils.config import settings

# Local modules

SCOPES = ["playlist-read-private"]  # Required scopes for the Spotify API

session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.CLIENT_ID,
                                                    client_secret=settings.CLIENT_SECRET, redirect_uri=settings.REDIRECT_URI, scope=",".join(SCOPES), cache_path='cache.txt'))
