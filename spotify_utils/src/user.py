from spotify_utils.src.auth import session


def get_details():
    return session.current_user()
