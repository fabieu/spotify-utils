# Built-in modules

# PyPi modules
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_utils.config import settings

# Local modules

AUTH_REDIRECT_URI = "http://localhost:60011"  # Redirect URL for the Spotify Authorization Code Flow
SCOPES = ["playlist-read-private"]  # Required scopes for the Spotify API

session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.CLIENT_ID,
                                                    client_secret=settings.CLIENT_SECRET, redirect_uri=AUTH_REDIRECT_URI, scope=",".join(SCOPES)))
