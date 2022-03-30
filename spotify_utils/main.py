from typing import Type
import typer
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import settings

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.SPOTIPY_CLIENT_ID,
                     client_secret=settings.SPOTIPY_CLIENT_SECRET, redirect_uri=settings.SPOTIPY_REDIRECT_URI, scope=settings.SCOPE))


def main():
    test = sp.current_user_playlists()
    print(test)


if __name__ == "__main__":
    typer.run(main)
