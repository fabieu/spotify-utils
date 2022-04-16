import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_utils.config import settings

session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.SPOTIPY_CLIENT_ID,
                                                    client_secret=settings.SPOTIPY_CLIENT_SECRET, redirect_uri=settings.SPOTIPY_REDIRECT_URI, scope=settings.SCOPE))
