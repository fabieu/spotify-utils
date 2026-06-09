from spotify_utils.src.auth import get_session


def get_details():
    return get_session().current_user()
