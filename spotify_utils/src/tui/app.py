"""
TUI for spotify-utils powered by Textual.

Launch with:  spotify-utils tui
"""
from __future__ import annotations

import importlib.metadata
import json
import uuid
import webbrowser
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from spotify_utils.src import file_engine, template_engine
from spotify_utils.src import user as user_module
from spotify_utils.src.auth import session
from spotify_utils.src.playlists import collect_playlists

__version__ = importlib.metadata.version("spotify-utils")


def _fmt_duration(ms: int) -> str:
    total_seconds = ms // 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def _pad(s: str, width: int) -> str:
    """Pad string to `width` code points (1 per character, matching Windows Terminal's
    single-cell rendering of emoji such as 🌛 that wcwidth counts as 2)."""
    return s + " " * max(0, width - len(s))


# ---------------------------------------------------------------------------
# Playlist tracks screen
# ---------------------------------------------------------------------------

class PlaylistTracksScreen(Screen[None]):
    """Detail screen listing all tracks of a single playlist."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, playlist_id: str, playlist_name: str, playlist_url: str) -> None:
        super().__init__()
        self._playlist_id = playlist_id
        self._playlist_name = playlist_name
        self._playlist_url = playlist_url

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(self._playlist_name, id="tracks-title"),
            Button("Open in Browser", id="tracks-open-url", variant="default"),
            id="tracks-header",
        )
        yield LoadingIndicator(id="tracks-loading")
        yield DataTable(id="tracks-table", cursor_type="row")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tracks-open-url":
            webbrowser.open(self._playlist_url)

    def on_mount(self) -> None:
        self.query_one("#tracks-loading", LoadingIndicator).display = False
        self._fetch()

    @work(thread=True)
    def _fetch(self) -> None:
        self.app.call_from_thread(self._set_loading, True)
        try:
            tracks_page = session.playlist_tracks(self._playlist_id)
            rows: list[tuple[str, str, str, str, str]] = []
            i = 1
            while tracks_page:
                for item in tracks_page["items"]:
                    track = item.get("track")
                    if not track:
                        continue
                    name = track.get("name", "")
                    artists = ", ".join(
                        a["name"] for a in track.get("artists", [])
                    )
                    album = track.get("album", {}).get("name", "")
                    duration = _fmt_duration(track.get("duration_ms", 0))
                    rows.append((str(i), name, artists, album, duration))
                    i += 1
                if tracks_page["next"]:
                    tracks_page = session.next(tracks_page)
                else:
                    break

            title_w = max((len(r[1]) for r in rows), default=5)
            artist_w = max((len(r[2]) for r in rows), default=9)
            album_w = max((len(r[3]) for r in rows), default=5)

            def populate() -> None:
                table = self.query_one(DataTable)
                table.add_column("#")
                table.add_column("Title")
                table.add_column("Artist(s)")
                table.add_column("Album")
                table.add_column("Duration")
                table.add_rows([
                    (r[0], _pad(r[1], title_w), _pad(r[2], artist_w), _pad(r[3], album_w), r[4])
                    for r in rows
                ])

            self.app.call_from_thread(populate)
        except Exception as exc:
            self.app.call_from_thread(self.app.notify, str(exc), severity="error")
        finally:
            self.app.call_from_thread(self._set_loading, False)

    def _set_loading(self, loading: bool) -> None:
        table = self.query_one(DataTable)
        self.query_one("#tracks-loading", LoadingIndicator).display = loading
        table.display = not loading
        if not loading:
            table.focus()


# ---------------------------------------------------------------------------
# Playlists tab
# ---------------------------------------------------------------------------

class PlaylistsTab(Container):
    """Lists the current user's playlists in a scrollable table."""

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="playlists-loading")
        yield DataTable(id="playlists-table", cursor_type="row")
        yield Horizontal(
            Button("Refresh", id="playlists-refresh", variant="primary"),
            id="playlists-actions",
        )

    def on_mount(self) -> None:
        self._playlist_data: dict[str, str] = {}  # id -> name
        self._playlist_urls: dict[str, str] = {}  # id -> url
        self._fetch()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "playlists-refresh":
            self._fetch(force_refresh=True)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        playlist_id = str(event.row_key.value)
        playlist_name = self._playlist_data.get(playlist_id, playlist_id)
        playlist_url = self._playlist_urls.get(playlist_id, "")
        self.app.push_screen(PlaylistTracksScreen(playlist_id, playlist_name, playlist_url))

    @work(thread=True)
    def _fetch(self, force_refresh: bool = False) -> None:
        self.app.call_from_thread(self._set_loading, True)
        try:
            playlists = self.app.get_playlists(force_refresh=force_refresh)
            rows: list[tuple[str, str, str]] = []
            playlist_data: dict[str, str] = {}
            playlist_urls: dict[str, str] = {}
            for p in playlists:
                playlist_data[p["id"]] = p["name"]
                playlist_urls[p["id"]] = p["external_urls"]["spotify"]
                rows.append((
                    p["name"],
                    p["owner"]["display_name"],
                    p["id"],
                ))

            name_w = max((len(r[0]) for r in rows), default=4)
            owner_w = max((len(r[1]) for r in rows), default=5)

            self._playlist_data = playlist_data
            self._playlist_urls = playlist_urls

            def populate() -> None:
                table = self.query_one(DataTable)
                table.clear(columns=True)
                table.add_column("Name")
                table.add_column("Owner")
                table.add_column("ID")
                for row in rows:
                    table.add_row(
                        _pad(row[0], name_w),
                        _pad(row[1], owner_w),
                        row[2],
                        key=row[2],
                    )

            self.app.call_from_thread(populate)
        except Exception as exc:
            self.app.call_from_thread(self.app.notify, str(exc), severity="error")
        finally:
            self.app.call_from_thread(self._set_loading, False)

    def _set_loading(self, loading: bool) -> None:
        self.query_one("#playlists-loading", LoadingIndicator).display = loading
        self.query_one(DataTable).display = not loading
        self.query_one("#playlists-refresh", Button).disabled = loading


# ---------------------------------------------------------------------------
# Export tab
# ---------------------------------------------------------------------------

class ExportTab(Container):
    """Exports one or all playlists to JSON or HTML."""

    def compose(self) -> ComposeResult:
        yield Label("Playlist:")
        yield Select(
            [],
            prompt="Loading playlists…",
            id="export-playlist-select",
        )
        yield Label("Format:")
        yield Select(
            [("JSON", "json"), ("HTML", "html")],
            prompt="Select a format…",
            id="export-format",
        )
        yield Label("Output directory:")
        yield Input(value=str(Path.cwd()), id="export-path")
        yield Horizontal(
            Button("Export", id="export-btn", variant="primary"),
            id="export-actions",
        )
        yield LoadingIndicator(id="export-loading")
        yield Static("", id="export-status")

    def on_mount(self) -> None:
        self.query_one("#export-loading", LoadingIndicator).display = False
        self._load_playlists()

    @work(thread=True)
    def _load_playlists(self) -> None:
        try:
            playlists = self.app.get_playlists()
            options: list[tuple[str, str]] = [("All Playlists", "")]
            for p in playlists:
                options.append((p["name"], p["id"]))

            def populate() -> None:
                select = self.query_one("#export-playlist-select", Select)
                select.set_options(options)
                select.value = ""  # pre-select "All Playlists"

            self.app.call_from_thread(populate)
        except Exception as exc:
            self.app.call_from_thread(self.app.notify, str(exc), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export-btn":
            self._export()

    @work(thread=True)
    def _export(self) -> None:
        playlist_value = self.query_one("#export-playlist-select", Select).value
        if playlist_value is Select.BLANK:
            self.app.call_from_thread(
                self.app.notify,
                "Please select a playlist.",
                severity="warning",
            )
            return
        playlist_id: str | None = playlist_value or None  # "" → None exports all
        fmt = self.query_one("#export-format", Select).value
        out_dir = Path(self.query_one("#export-path", Input).value.strip())

        if fmt is Select.BLANK:
            self.app.call_from_thread(
                self.app.notify,
                "Please select an export format.",
                severity="warning",
            )
            return

        self.app.call_from_thread(self._set_loading, True, "Collecting playlists…")
        try:
            playlists_data = collect_playlists(session, playlist_id)
            self.app.call_from_thread(self._set_status, "Writing file…")

            stem = out_dir / f"playlist_export_{uuid.uuid4()}"
            if fmt == "json":
                outpath = stem.with_suffix(".json")
                file_engine.write_file(json.dumps(playlists_data, indent=2), outpath)
            else:
                outpath = stem.with_suffix(".html")
                file_engine.write_file(
                    template_engine.render_playlist_export(playlists_data), outpath
                )

            self.app.call_from_thread(self._set_status, f"Saved: {outpath}")
            self.app.call_from_thread(
                self.app.notify,
                f"Export complete → {outpath.name}",
                severity="information",
            )
        except Exception as exc:
            self.app.call_from_thread(self._set_status, f"Error: {exc}")
            self.app.call_from_thread(self.app.notify, str(exc), severity="error")
        finally:
            self.app.call_from_thread(self._set_loading, False, "")

    def _set_loading(self, loading: bool, status: str = "") -> None:
        self.query_one("#export-loading", LoadingIndicator).display = loading
        self.query_one("#export-btn", Button).disabled = loading
        if status:
            self.query_one("#export-status", Static).update(status)

    def _set_status(self, message: str) -> None:
        self.query_one("#export-status", Static).update(message)


# ---------------------------------------------------------------------------
# Duplicates tab
# ---------------------------------------------------------------------------

class DuplicatesTab(Container):
    """Scans owned playlists for duplicate tracks."""

    def on_mount(self) -> None:
        self._scanned = False
        table = self.query_one(DataTable)
        table.add_columns("Track", "Artists", "Found in Playlists")
        table.display = False
        self.query_one("#dup-loading", LoadingIndicator).display = False

    def compose(self) -> ComposeResult:
        yield Static(
            "Click [bold]Scan[/bold] to find duplicate tracks across your owned playlists.",
            id="dup-stats",
        )
        yield Horizontal(
            Button("Scan", id="dup-scan-btn", variant="primary"),
            id="dup-actions",
        )
        yield LoadingIndicator(id="dup-loading")
        yield DataTable(id="dup-table", cursor_type="row")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dup-scan-btn":
            self._scan()

    @work(thread=True)
    def _scan(self) -> None:
        self.app.call_from_thread(self._set_scanning, True)
        table = self.query_one(DataTable)
        self.app.call_from_thread(table.clear)
        try:
            current_user = user_module.get_details()
            owned = [
                p for p in self.app.get_playlists()
                if p["owner"]["id"] == current_user["id"]
            ]

            tracks_map: dict[str, list[str]] = {}
            for playlist in owned:
                tracks_page = session.playlist_items(playlist["id"])
                while tracks_page:
                    for item in tracks_page["items"]:
                        if item["track"] and item["track"].get("id"):
                            tid = item["track"]["id"]
                            tracks_map.setdefault(tid, []).append(playlist["id"])
                    if tracks_page["next"]:
                        tracks_page = session.next(tracks_page)
                    else:
                        break

            duplicates = {
                tid: pids for tid, pids in tracks_map.items() if len(pids) > 1
            }

            rows: list[tuple[str, str, str]] = []
            playlist_cache: dict[str, str] = {}
            for tid, pids in duplicates.items():
                track = session.track(tid)
                track_name = track["name"]
                artists = ", ".join(a["name"] for a in track["artists"])
                p_names: list[str] = []
                for pid in pids:
                    if pid not in playlist_cache:
                        playlist_cache[pid] = session.playlist(pid, fields="name")["name"]
                    p_names.append(playlist_cache[pid])
                rows.append((track_name, artists, ", ".join(p_names)))

            count = len(duplicates)
            if count > 0:
                stats = (
                    f"Found [bold red]{count}[/bold red] duplicate track(s) "
                    f"across [bold]{len(owned)}[/bold] owned playlist(s)."
                )
            else:
                stats = (
                    f"[bold green]No duplicates found[/bold green] "
                    f"across [bold]{len(owned)}[/bold] owned playlist(s)."
                )

            self.app.call_from_thread(self._update_stats, stats)
            self.app.call_from_thread(table.add_rows, rows)
        except Exception as exc:
            self.app.call_from_thread(self.app.notify, str(exc), severity="error")
        finally:
            self.app.call_from_thread(self._set_scanning, False)

    def _set_scanning(self, scanning: bool) -> None:
        self.query_one("#dup-loading", LoadingIndicator).display = scanning
        self.query_one("#dup-scan-btn", Button).disabled = scanning
        if not scanning:
            self._scanned = True
        self.query_one(DataTable).display = self._scanned and not scanning

    def _update_stats(self, message: str) -> None:
        self.query_one("#dup-stats", Static).update(message)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class SpotifyUtilsApp(App[None]):
    TITLE = f"spotify-utils v{__version__}"
    CSS_PATH = "tui.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+l", "switch_tab('tab-playlists')", "Playlists", priority=True),
        Binding("ctrl+e", "switch_tab('tab-export')", "Export", priority=True),
        Binding("ctrl+d", "switch_tab('tab-duplicates')", "Duplicates", priority=True),
    ]

    _playlists_cache: list[dict] | None = None

    def get_playlists(self, force_refresh: bool = False) -> list[dict]:
        """Return cached playlist list, fetching from the API when necessary."""
        if self._playlists_cache is None or force_refresh:
            page = session.current_user_playlists()
            playlists: list[dict] = []
            while page:
                playlists.extend(page["items"])
                if page["next"]:
                    page = session.next(page)
                else:
                    break
            self._playlists_cache = playlists
        return self._playlists_cache

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Playlists", id="tab-playlists"):
                yield PlaylistsTab()
            with TabPane("Duplicates", id="tab-duplicates"):
                yield DuplicatesTab()
            with TabPane("Export", id="tab-export"):
                yield ExportTab()
        yield Footer()


def main() -> None:
    """Entry point for the spotify-utils TUI."""
    SpotifyUtilsApp().run()


if __name__ == "__main__":
    main()
