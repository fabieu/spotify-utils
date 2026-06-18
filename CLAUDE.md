# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`spotify-utils` is a Python CLI (Typer) + TUI (Textual) for Spotify utility tasks: listing playlists, exporting them (JSON/HTML), and finding duplicate tracks. Packaged with Poetry and published to PyPI. Python 3.10+.

## Commands

```bash
poetry install                       # set up the venv with all deps
poetry run spotify-utils <command>   # run the CLI from source (e.g. `playlists list`, `tui`, `version`)
poetry run pytest                    # run tests (note: no test suite exists yet despite pytest being a dev dep)
poetry build                         # build the sdist/wheel
```

There is no linter configured. CI (`.github/workflows/build.yml`) is manual (`workflow_dispatch`) and only builds + publishes to PyPI via Trusted Publisher; it does not run tests.

## Configuration & auth

Credentials are required for any command that hits the Spotify API: `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`. They are supplied via env vars prefixed `SPOTIFY_UTILS_`, a `.env` file, or `spotify_utils/.secrets.toml` / `spotify_utils/settings.toml`.

`config.py` sets `root_path=Path(__file__).parent` on Dynaconf so the relative `settings_files` resolve against the **package directory**, not the current working directory — this is what lets the installed CLI find config regardless of where it's launched from. Don't remove it.

## Architecture

**Entry point:** `spotify_utils/main.py` builds the root Typer `app`, registers the `playlists` sub-app, and defines `version` and `tui` commands. `pyproject.toml` maps the `spotify-utils` script to `spotify_utils.main:main` — a thin wrapper around `app()` that catches `AuthenticationError` (from `src/auth.py`) and turns it into a stderr message + exit code 1 instead of a traceback.

**Lazy authentication (important invariant):** `src/auth.py` exposes `get_session() -> spotipy.Spotify`, a memoized factory backed by a module-level `_session` + `_session_lock` (double-checked locking, **not** `@cache` — `lru_cache` doesn't serialize concurrent first calls, and the TUI calls `get_session()` from several worker threads at once, which would launch multiple sign-in flows). Credentials are read on the *first call*, not at import time, so `--help` and `version` work without any config. **Never call `get_session()` (or otherwise read `settings.CLIENT_ID` etc.) at module level / import time** — doing so reintroduces eager auth and breaks `--help`. Inside functions, bind `session = get_session()` once and reuse it.

`get_session()` also recovers from expired refresh tokens: on first call it validates the cached token, and on an `invalid_grant` it discards the dead token and re-runs the sign-in flow once (never retries the failed refresh). If that re-sign-in fails it raises `AuthenticationError` — a UI-agnostic exception the CLI wrapper and TUI present in their own way. Don't reintroduce `typer.echo`/`typer.Exit` into `auth.py`; it's shared with the TUI, where Typer's exit machinery is meaningless.

**Spotify pagination pattern:** the Spotify API returns paginated results. The repeated idiom across the codebase is `while page: ...; page = session.next(page) if page['next'] else break`. Preserve this when adding new API traversals.

**Code layout under `spotify_utils/src/`:**
- `playlists.py` — the `playlists` Typer sub-app (`list`, `export`, `duplicates`) plus the CLI's collection/dedup helpers.
- `user.py` — thin wrapper for current-user details.
- `template_engine.py` — Jinja2 HTML export; loads templates via `PackageLoader("spotify_utils")` from `spotify_utils/templates/` (`playlist_export.html`). Registers `extract_artists` / `duration` filters.
- `file_engine.py` — file writing for exports.
- `enums.py` — `OutputFormat` (html/json) and `OutputFormatJson` for Typer option choices.
- `tui/app.py` — the entire Textual TUI.

**TUI specifics (`src/tui/app.py`):** a `SpotifyUtilsApp` with tabbed panes (Playlists / Duplicates / Export) and a `PlaylistTracksScreen` detail screen. All Spotify API calls run inside `@work(thread=True)` workers so the UI never blocks; results are pushed back to widgets via `self.app.call_from_thread(...)`. Note the TUI re-implements some helpers (e.g. `_build_tracks_map`, duplicate-row building) independently of `playlists.py` rather than importing them — if you change dedup/collection logic, check both places.
