import spotipy
from spotify_utils.config import settings
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

SCOPES = ["playlist-read-private"]  # Required scopes for the Spotify API

cache_path = "cache.json"

# Create cache file from environment variable for automatic CI testing. Do not use in production!
if settings.CACHE:
    with open(cache_path, "w") as f:
        f.write(settings.CACHE)

cache_handler = CacheFileHandler(cache_path=cache_path)
session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.CLIENT_ID,
                                                    client_secret=settings.CLIENT_SECRET,
                                                    redirect_uri=settings.REDIRECT_URI,
                                                    scope=",".join(SCOPES),
                                                    cache_handler=cache_handler))
