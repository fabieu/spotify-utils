# Built-in modules
from pathlib import Path
from typing import Optional

# PyPi modules
import typer
import click_spinner
from tabulate import tabulate
import spotipy.exceptions

# Local modules
from spotify_utils.src.auth import session
from spotify_utils.src import user

# Initialize Typer
app = typer.Typer()


@app.command()
def list():
    """
    List all playlists of the current user
    """
    playlists = session.current_user_playlists()
    table = []
    while playlists:
        for playlist in playlists['items']:
            playlist_name = playlist['name']
            playlist_owner = playlist['owner']['display_name']
            playlist_url = playlist['external_urls']['spotify']
            playlist_id = playlist['id']
            table.append([playlist_name, playlist_owner, playlist_id, playlist_url])
        if playlists['next']:
            playlists = session.next(playlists)
        else:
            break

    typer.echo(tabulate(table, headers=["name", "owner", "id", "url"], showindex=True, tablefmt="simple"))


@app.command()
def duplicates(verbose: bool = typer.Option(False, "--verbose", "-v")):
    """
    Find duplicates in playlists which are owned by the current user
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
            break

    seen_tracks = set()
    duplicate_tracks = []

    for playlist in owned_playlists:
        with click_spinner.spinner():
            tracks = session.playlist_items(playlist['id'])

            # Check if track has already been seen - Uniqueness based on track id
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
                    break

    if duplicate_tracks:
        duplicates_count = typer.style(len(duplicate_tracks), fg=typer.colors.RED)
    else:
        duplicates_count = typer.style("no", fg=typer.colors.GREEN)

    typer.echo(f"Found {duplicates_count} duplicate tracks across {len(owned_playlists)} playlists")

    if verbose:
        for track in duplicate_tracks:
            typer.echo(f"- {track['track']['name']}")


@app.command()
def export(
    playlist_id: Optional[str] = typer.Argument(None, help="Spotify playlist ID"),
    csv: bool = typer.Option(False, "--csv", help="Export playlist(s) to CSV"),
    json: bool = typer.Option(False, "--json", help="Export playlist(s) to JSON"),
    html: bool = typer.Option(False, "--html", help="Export playlist(s) to HTML"),
    path: Path = typer.Option(
        Path().cwd(), help="Set the output path for all file based output options"
    ),
):
    """
    Export all (default) playlists or a specific playlist to the chosen output format(s)
    """
    export_list = []

    if playlist_id:
        try:
            export_list.append(session.playlist(playlist_id))
        except spotipy.exceptions.SpotifyException as e:
            typer.secho(str(e), fg=typer.colors.RED, err=True)
    else:
        playlists = session.current_user_playlists()
        while playlists:
            for playlist in playlists['items']:
                export_list.append(playlist)
            if playlists['next']:
                playlists = session.next(playlists)
            else:
                break

    print(export_list)
