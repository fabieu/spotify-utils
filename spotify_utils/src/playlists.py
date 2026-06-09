import json
import uuid
from pathlib import Path
from typing import Optional

import spotipy.exceptions
import typer
from tabulate import tabulate

from spotify_utils.src import user, template_engine, file_engine
from spotify_utils.src.auth import get_session
from spotify_utils.src.enums import OutputFormat, OutputFormatJson

# Initialize Typer
app = typer.Typer()


@app.command(name="list")
def list_playlists(
        format: OutputFormatJson = typer.Option(None, help="Output the response in JSON format")
):
    """
    List all playlists of the user
    """
    session = get_session()
    playlists = session.current_user_playlists()
    playlists_list = []
    table = {}
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

    if format == OutputFormatJson.JSON:
        typer.echo(json.dumps(playlists_list, indent=2))
    else:
        typer.echo(tabulate(table, headers="keys", showindex=True, tablefmt="simple"))

    return playlists_list


@app.command()
def export(
        playlist_id: Optional[str] = typer.Option(None, "--id", help="Spotify playlist ID"),
        format: OutputFormat = typer.Option(None, case_sensitive=False, help="Define the output format"),
        path: Path = typer.Option(
            Path().cwd(), help="Set the output path for all file based output options"
        ),

):
    """
    Export all playlists of the user (default) or a specific playlist by ID in the specified format.
    """
    playlists_with_tracks = collect_playlists(get_session(), playlist_id)

    match format:
        case OutputFormat.JSON:
            outpath = path / f"playlist_export_{uuid.uuid4()}.json"
            file_engine.write_file(json.dumps(playlists_with_tracks, indent=2), outpath)
        case OutputFormat.HTML:
            outpath = path / f"playlist_export_{uuid.uuid4()}.html"
            file_engine.write_file(template_engine.render_playlist_export(playlists_with_tracks), outpath)
        case _:
            typer.secho("Unsupported format. Please provide one of json or html", fg=typer.colors.RED, err=True)


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
    session = get_session()
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


def _get_owned_playlists(current_user: dict) -> list:
    """Return all playlists owned by current_user."""
    session = get_session()
    owned = []
    playlists = session.current_user_playlists()
    while playlists:
        for playlist in playlists['items']:
            if current_user['id'] == playlist['owner']['id']:
                owned.append(playlist)
        if playlists['next']:
            playlists = session.next(playlists)
        else:
            break
    return owned


def _build_tracks_map(owned_playlists: list) -> dict:
    """Return a map of track_id → [playlist_id, ...] across all owned playlists."""
    session = get_session()
    tracks_map = {}
    for playlist in owned_playlists:
        tracks = session.playlist_items(playlist['id'])
        while tracks:
            for track in tracks['items']:
                tracks_map.setdefault(track['track']['id'], []).append(playlist['id'])
            if tracks['next']:
                tracks = session.next(tracks)
            else:
                break
    return tracks_map


def find_unavailable_tracks(playlists: list[dict]) -> list[dict]:
    """
    Scan the given playlists for tracks that are removed from Spotify or
    unavailable (greyed out) in the user's market.

    Detection requires market-scoped requests (the user's ISO 3166-1 alpha-2
    country code, resolved from their profile):
      - ``item['track']`` is ``None`` → the track was removed from Spotify.
      - ``track['is_playable']`` is ``False`` → unavailable in the user's market;
        ``track['restrictions']['reason']`` explains why (market/product/explicit).

    Returns a list of dicts with keys: name, artists, playlist, reason.
    """
    session = get_session()
    market = user.get_details().get('country')

    results: list[dict] = []
    seen: set[tuple[str, str]] = set()  # (playlist_id, track_id) — collapse repeated copies
    for playlist in playlists:
        tracks = session.playlist_items(playlist['id'], market=market)
        while tracks:
            for item in tracks['items']:
                track = item.get('track')
                if track is None:
                    results.append({
                        "name": "(removed track)",
                        "artists": "",
                        "playlist": playlist['name'],
                        "reason": "removed",
                    })
                    continue
                if track.get('is_playable') is False:
                    track_id = track.get('id')
                    if track_id:
                        key = (playlist['id'], track_id)
                        if key in seen:
                            continue
                        seen.add(key)
                    reason = (track.get('restrictions') or {}).get('reason', "unavailable")
                    results.append({
                        "name": track.get('name', ""),
                        "artists": ", ".join(a['name'] for a in track.get('artists', [])),
                        "playlist": playlist['name'],
                        "reason": reason,
                    })
            if tracks['next']:
                tracks = session.next(tracks)
            else:
                break
    return results


@app.command()
def unavailable(
        verbose: bool = typer.Option(False, "--verbose", "-v"),
        quiet: bool = typer.Option(False, "--quiet", "-q")
):
    """
    Find tracks that are removed or unavailable (greyed out) in playlists owned by the current user
    """
    current_user = user.get_details()
    owned_playlists = _get_owned_playlists(current_user)
    unavailable_tracks = find_unavailable_tracks(owned_playlists)

    # Print basic stats, like number of unavailable tracks and searched playlists to console
    if not quiet:
        if unavailable_tracks:
            unavailable_count = typer.style(len(unavailable_tracks), fg=typer.colors.RED)
        else:
            unavailable_count = typer.style("0", fg=typer.colors.GREEN)

        typer.echo(f"Found {unavailable_count} unavailable tracks across {len(owned_playlists)} playlists")

    # Print additional information about the unavailable tracks and their playlists
    if verbose and not quiet and unavailable_tracks:
        table = {}
        for entry in unavailable_tracks:
            table.setdefault("name", []).append(entry['name'])
            table.setdefault("artists", []).append(entry['artists'])
            table.setdefault("playlist", []).append(entry['playlist'])
            table.setdefault("reason", []).append(entry['reason'])

        typer.echo(tabulate(table, headers="keys", showindex=True, tablefmt="simple"))


@app.command()
def duplicates(
        verbose: bool = typer.Option(False, "--verbose", "-v"),
        quiet: bool = typer.Option(False, "--quiet", "-q")
):
    """
    Find duplicates in playlists which are owned by the current user
    """
    session = get_session()
    current_user = user.get_details()
    owned_playlists = _get_owned_playlists(current_user)
    tracks_map = _build_tracks_map(owned_playlists)

    duplicate_tracks = {tid: pids for tid, pids in tracks_map.items() if len(pids) > 1}

    # Print basic stats, like number of duplicates and searched playlists to console
    if not quiet:
        if duplicate_tracks:
            duplicate_tracks_count = typer.style(len(duplicate_tracks), fg=typer.colors.RED)
        else:
            duplicate_tracks_count = typer.style("0", fg=typer.colors.GREEN)

        typer.echo(f"Found {duplicate_tracks_count} duplicate tracks across {len(owned_playlists)} playlists")

    # Print additional information about the duplicate tracks and the playlists
    if verbose and not quiet:
        table = {}

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
