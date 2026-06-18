import threading

import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

from spotify_utils.config import settings

SCOPES = [
    "playlist-read-private",
    "user-read-private"
]


class AuthenticationError(Exception):
    """A Spotify sign-in is required but could not be completed.

    UI-agnostic on purpose: the CLI turns it into a stderr message + exit code,
    the TUI shows it in the auth-status indicator.
    """


_session: spotipy.Spotify | None = None
_session_lock = threading.Lock()


def get_session() -> spotipy.Spotify:
    """Build (once) and return the Spotify client. Credentials are read on first call.

    Thread-safe: the TUI calls this from several worker threads at once, so concurrent
    first callers serialize on a lock to guarantee a single sign-in flow.
    """
    global _session
    if _session is not None:
        return _session

    with _session_lock:
        if _session is not None:
            return _session

        auth_manager = SpotifyOAuth(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            scope=",".join(SCOPES),
            cache_handler=CacheFileHandler()
        )

        # Spotify refresh tokens expire (and a stale one yields invalid_grant). Discard the
        # dead token and re-run the sign-in flow once; never retry the failed refresh blindly.
        try:
            auth_manager.validate_token(auth_manager.cache_handler.get_cached_token())
        except SpotifyOauthError as error:
            if error.error != "invalid_grant":
                raise
            auth_manager.cache_handler.save_token_to_cache(None)
            try:
                auth_manager.get_access_token(check_cache=False)
            except SpotifyOauthError as exc:
                raise AuthenticationError(
                    "Your Spotify sign-in has expired and could not be renewed. "
                    "Please run the command again to sign in."
                ) from exc

        _session = spotipy.Spotify(auth_manager=auth_manager)
        return _session
