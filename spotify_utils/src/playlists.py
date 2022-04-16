# Built-in modules
from pathlib import Path
from tabnanny import verbose

# PyPi modules
import typer

# Local modules
from spotify_utils.src.auth import session
from spotify_utils.src import user

# Initialize Typer
app = typer.Typer()


@app.command()
def duplicates(verbose: bool = typer.Option(False, "--verbose", "-v")):
    """
    Find duplicates in playlists which are owned by the current authenticated user
    """
    current_user = user.get_details()

    playlists = session.current_user_playlists()
    owned_playlists = []
    while playlists:
        for playlist in playlists['items']:
            if current_user['uri'] == playlist['owner']['uri']:
                owned_playlists.append(playlist)
        if playlists['next']:
            playlists = session.next(playlists)
        else:
            playlists = None

    for playlist in owned_playlists:
        tracks = session.playlist_items(playlist['id'])

        seen_tracks = set()
        duplicate_tracks = []

        while tracks:
            for track in tracks['items']:
                track_id = track['track']['id']
                if track_id not in seen_tracks:
                    seen_tracks.add(track_id)
                else:
                    duplicate_tracks.append(track)
            if tracks['next']:
                tracks = session.next(tracks)
            else:
                tracks = None

        if duplicate_tracks:
            typer.echo(f"Found {len(duplicate_tracks)} duplicate tracks in playlist '{playlist.get('name')}'")

            if verbose:
                for i, track in enumerate(duplicate_tracks):
                    typer.echo(f"{i + 1} {track['track']['name']}")


@app.command()
def export(
    playlist_name: str = typer.Argument(...),
    csv: bool = typer.Option(False, "--csv", help="Export playlist(s) to CSV"),
    json: bool = typer.Option(False, "--json", help="Export playlist(s) to JSON"),
    html: bool = typer.Option(False, "--html", help="Export playlist(s) to HTML"),
    path: Path = typer.Option(
        Path().cwd(), help="Sets the output path for all file based output options"
    )
):
    pass
