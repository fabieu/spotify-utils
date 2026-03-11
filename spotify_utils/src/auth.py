import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

from spotify_utils.config import settings

SCOPES = ["playlist-read-private"]  # Required scopes for the Spotify API


class _LazySession:
    """Defers Spotipy session creation until settings are available."""

    _session: spotipy.Spotify | None = None

    def _get(self) -> spotipy.Spotify:
        if self._session is None:
            self._session = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=settings.CLIENT_ID,
                    client_secret=settings.CLIENT_SECRET,
                    redirect_uri=settings.REDIRECT_URI,
                    scope=",".join(SCOPES),
                    cache_handler=CacheFileHandler(),
                )
            )
        return self._session

    def reset(self) -> None:
        """Discard the cached session so it is recreated on next access."""
        self._session = None

    def __getattr__(self, name: str):
        return getattr(self._get(), name)


session = _LazySession()
