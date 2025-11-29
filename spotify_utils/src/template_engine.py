import math
from datetime import timedelta

from jinja2 import Environment, PackageLoader, select_autoescape


def render_playlist_export(playlists: list) -> str:
    def extract_artists(track):
        """
        Extract artists from track object to a single string
        """
        return ", ".join([artist['name'] for artist in track['artists']])

    def duration(milliseconds: int):
        """
        Format seconds to HH:MM:SS string
        """
        seconds = math.ceil(milliseconds / 1000)
        return str(timedelta(seconds=seconds))

    env = Environment(
        loader=PackageLoader("spotify_utils"),
        autoescape=select_autoescape()
    )
    env.filters['extract_artists'] = extract_artists
    env.filters['duration'] = duration

    template = env.get_template("playlist_export.html")

    return template.render(playlists=playlists)
