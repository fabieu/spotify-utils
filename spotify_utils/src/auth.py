# Built-in modules
import os

# PyPi modules
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Local modules
import spotify_utils.constants as CONSTANTS

session = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                                    client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], redirect_uri=CONSTANTS.SPOTIPY_REDIRECT_URI, scope=CONSTANTS.SCOPES))
