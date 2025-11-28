import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import spotipy.exceptions
import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from tabulate import tabulate

from spotify_utils.src import user
from spotify_utils.src.auth import session
from spotify_utils.src.file_operations import write_file

# Initialize Typer
app = typer.Typer()


@app.command(name="list")
def list_playlists(
        json_output: bool = typer.Option(False, "--json", help="Output the response in JSON format")
):
    """
    List all playlists of the current user
    """
    playlists = session.current_user_playlists()
    playlists_list = []
    table = dict()
    while playlists:
        for playlist in playlists['items']:
            table.setdefault("name", []).append(playlist['name'])
            table.setdefault("owner", []).append(playlist['owner']['display_name'])
            table.setdefault("id", []).append(playlist['id'])
            table.setdefault("url", []).append(playlist['external_urls']['spotify'])
            playlists_list.append(playlist)
        if playlists['next']:
            playlists = session.next(playlists)
        else:
            break

    if json_output:
        typer.echo(json.dumps(playlists_list))
    else:
        typer.echo(tabulate(table, headers="keys", showindex=True, tablefmt="simple"))

    return playlists_list


@app.command()
def duplicates(
        verbose: bool = typer.Option(False, "--verbose", "-v"),
        quiet: bool = typer.Option(False, "--quiet", "-q")
):
    """
    Find duplicates in playlists which are owned by the current user
    """
    current_user = user.get_details()
    playlists = session.current_user_playlists()

    # Discover all playlists owned by the current user by comparing the "id" of the current user with the "id" of the playlist owner
    owned_playlists = []
    while playlists:
        for playlist in playlists['items']:
            if current_user['id'] == playlist['owner']['id']:
                owned_playlists.append(playlist)
        if playlists['next']:
            playlists = session.next(playlists)
        else:
            break

    # Iterate over all tracks from every playlists and create a HashMap with key = track id and value = all playlist ids where the track has been found
    tracks_map = dict()

    for playlist in owned_playlists:
        tracks = session.playlist_items(playlist['id'])

        while tracks:
            for track in tracks['items']:
                track_id = track['track']['id']
                tracks_map.setdefault(track_id, []).append(playlist['id']),
            if tracks['next']:
                tracks = session.next(tracks)
            else:
                break

    # Filter tracks_map for tracks with more than one playlist_id (duplicates)
    duplicate_tracks = dict()
    for track_id, playlist_ids in tracks_map.items():
        if len(playlist_ids) > 1:
            duplicate_tracks[track_id] = playlist_ids

    # Print basic stats, like number of duplicates and searched playlists to console
    if not quiet:
        if duplicate_tracks:
            duplicate_tracks_count = typer.style(len(duplicate_tracks), fg=typer.colors.RED)
        else:
            duplicate_tracks_count = typer.style("0", fg=typer.colors.GREEN)

        typer.echo(f"Found {duplicate_tracks_count} duplicate tracks across {len(owned_playlists)} playlists")

    # Print additional information about the duplicate tracks and the playlists
    if verbose and not quiet:
        table = dict()

        for track_id, playlist_ids in duplicate_tracks.items():
            track_details = session.track(track_id)

            playlist_names_list = []
            for playlist_id in playlist_ids:
                playlist_details = session.playlist(playlist_id)
                playlist_names_list.append(playlist_details['name'])

            table.setdefault("name", []).append(track_details['name'])
            table.setdefault("artists", []).append(", ".join([artist['name']
                                                              for artist in track_details['artists']]))
            table.setdefault("playlists", []).append(", ".join(playlist_names_list))
            table.setdefault("track_id", []).append(track_id)

        typer.echo(tabulate(table, headers="keys", showindex=True, tablefmt="simple"))


@app.command()
def export(
        playlist_id: Optional[str] = typer.Argument(None, help="Spotify playlist ID"),
        json_out: bool = typer.Option(False, "--json", help="Export playlist(s) to JSON"),
        html_out: bool = typer.Option(False, "--html", help="Export playlist(s) to HTML"),
        launch: bool = typer.Option(True, help="Open export file automatically"),
        path: Path = typer.Option(
            Path().cwd(), help="Set the output path for all file based output options"
        ),

):
    """
    Export all playlists (default) or a specific playlist to the chosen output format(s)
    """
    playlists_with_tracks = collect_playlists(session, playlist_id)

    if json_out:
        path.mkdir(parents=True, exist_ok=True)
        outpath = path / f"playlist_export_{date.today()}.json"
        write_file(json.dumps(playlists_with_tracks, indent=2), outpath)

        if launch:
            typer.launch(str(outpath))  # Open file in default application
    elif html_out:
        path.mkdir(parents=True, exist_ok=True)
        outpath = path / f"playlist_export_{date.today()}.html"
        write_file(format_html(playlists_with_tracks, "playlists.html"), outpath)

        if launch:
            typer.launch(str(outpath))  # Open file in default application
    else:
        typer.secho("Missing output parameter. Please provide one of --json or --html",
                    fg=typer.colors.RED, err=True)


def collect_playlists(session: spotipy.Spotify, playlist_id: str | None = None):
    """
    Return a list of full playlist objects.

    - If playlist_id is provided: return just that playlist.
    - Otherwise: return all of the current user's playlists.
    """
    playlist_objects: list[dict] = []

    try:
        # Single playlist by id
        if playlist_id:
            playlist_objects.append(fetch_full_playlist(playlist_id))
            return playlist_objects

        # All playlists of current user
        playlists = session.current_user_playlists()
        while playlists:
            for playlist in playlists.get('items', []):
                playlist_objects.append(fetch_full_playlist(playlist['id']))

            if playlists.get('next'):
                playlists = session.next(playlists)
            else:
                break

    except spotipy.exceptions.SpotifyException as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)

    return playlist_objects


def fetch_full_playlist(playlist_id: str):
    """
    Return playlist object with all tracks loaded (paginated).
    """
    playlist = session.playlist(playlist_id)
    all_items = []

    tracks = session.playlist_tracks(playlist_id)
    while tracks:
        for item in tracks.get('items', []):
            all_items.append(item)

        if tracks.get('next'):
            tracks = session.next(tracks)
        else:
            break

    # normalize playlist['tracks'] to include the full items and total count
    playlist['tracks'] = {'items': all_items, 'total': len(all_items)}
    return playlist


def format_html(playlists: list, template_name: str):
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

    template = env.get_template(template_name)
    template.globals['now'] = datetime.now()

    return template.render(playlists=playlists)
