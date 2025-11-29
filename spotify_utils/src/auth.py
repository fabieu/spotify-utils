import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

from spotify_utils.config import settings

SCOPES = ["playlist-read-private"]  # Required scopes for the Spotify API

session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.CLIENT_ID,
                                                    client_secret=settings.CLIENT_SECRET,
                                                    redirect_uri=settings.REDIRECT_URI,
                                                    scope=",".join(SCOPES),
                                                    cache_handler=CacheFileHandler()))
