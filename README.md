<div id="top"></div>
<!-- PROJECT SHIELDS -->

[![GitHub Release](https://img.shields.io/github/v/release/fabieu/spotify-utils)](https://github.com/fabieu/spotify-utils/releases/latest)
[![GitHub Issues](https://img.shields.io/github/issues/fabieu/spotify-utils)](https://github.com/fabieu/spotify-utils/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/fabieu/spotify-utils)](https://github.com/fabieu/spotify-utils/pulls)
[![License](https://img.shields.io/github/license/fabieu/spotify-utils)](https://github.com/fabieu/spotify-utils/blob/main/LICENSE)

[![PyPI Version](https://img.shields.io/pypi/v/spotify-utils)](https://pypi.org/project/spotify-utils/)
[![Python Versions](https://img.shields.io/pypi/pyversions/spotify-utils)](https://pypi.org/project/spotify-utils/)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=alert_status)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=security_rating)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=reliability_rating)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=sqale_rating)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=vulnerabilities)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=fabieu_spotify-utils&metric=sqale_index)](https://sonarcloud.io/summary/overall?id=fabieu_spotify-utils)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/fabieu/spotify-utils">
    <img src="https://raw.githubusercontent.com/fabieu/spotify-utils/main/docs/logo.svg" alt="Logo" width="200" height="200">
  </a>

<h2 align="center">spotify-utils</h2>

  <p align="center">
    An awesome and easy-to-use CLI & TUI for various Spotify&reg; utility tasks!
    <br />
    <a href="https://github.com/fabieu/spotify-utils/issues">Report Bug</a>
    ·
    <a href="https://github.com/fabieu/spotify-utils/issues">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->

## About The Project

`spotify-utils` is a lightweight command-line tool that takes care of the Spotify&reg; housekeeping the official
clients don't. Authenticate once with your own Spotify&reg; app credentials and you get a fast, scriptable way to
inspect, export, and clean up your playlists — either from plain CLI commands or from an interactive terminal UI.

Everything talks directly to the Spotify&reg; Web API, output is available in formats you can pipe into other tools
(JSON) or hand to a human (console tables, HTML), and authentication is lazy so commands like `--help` and `version`
work without any configuration.

### Key features

- **Interactive TUI** — a [Textual](https://github.com/Textualize/textual)-based terminal UI with tabs for browsing
  playlists and their tracks, scanning for duplicates, finding unavailable tracks, and exporting — all fully keyboard
  navigable and non-blocking.
- **List playlists** — show every playlist of the authenticated user as a console table or as JSON.
- **Export playlists** — export all playlists or a single playlist by ID to JSON or to a self-contained HTML report.
- **Find duplicates** — scan your owned playlists for tracks that appear in more than one playlist, with an optional
  detailed breakdown of which playlists each duplicate lives in.
- **Find unavailable tracks** — detect tracks in your owned playlists that have been removed from Spotify&reg; or are
  greyed out (unavailable) in your market, including the reason why.

This CLI won't serve every need — more features are planned. Suggestions are welcome: fork the repo and open a pull
request, or open an issue.

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
pipx install spotify-utils
```

### Configuration

All methods require user authorization. You will need to register your app
at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) to get the credentials necessary
to make
authorized calls. [Click here](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/)
to go to
the step-by-step guide for creating a Spotify&reg; application.

The CLI uses the Authorization Code Flow, which the user logs into once. It provides an access token that can be
refreshed.

Environment variables are being used for configuration. In order for the CLI to function properly you need to provide
the following environment variables (use export instead of SET on Linux):

```powershell
set SPOTIFY_UTILS_CLIENT_ID='your-spotify-client-id'
set SPOTIFY_UTILS_CLIENT_SECRET='your-spotify-client-secret'
set SPOTIFY_UTILS_REDIRECT_URI='your-app-redirect-url'
```

In addition, the use of an `.env` file is supported:

```
SPOTIFY_UTILS_CLIENT_ID='your-spotify-client-id'
SPOTIFY_UTILS_CLIENT_SECRET='your-spotify-client-secret'
SPOTIFY_UTILS_REDIRECT_URI='your-app-redirect-url'
```

<!-- USAGE EXAMPLES -->

## Usage and examples

In this section you can find usage examples of the CLI

### Launch the interactive TUI

```text
spotify-utils tui
```

The TUI provides four tabs:

- **Playlists** — browse all your playlists in a table; click a row to view its tracks
- **Duplicates** — scan your owned playlists and list any duplicate tracks
- **Unavailable** — scan your owned playlists for removed or greyed-out tracks
- **Export** — select a playlist (or all), choose JSON or HTML, and pick an output directory

Key bindings: `Ctrl+L` Playlists · `Ctrl+D` Duplicates · `Ctrl+U` Unavailable · `Ctrl+E` Export · `Ctrl+Q` Quit

### List all playlists of the current user in JSON format

```text
spotify-utils playlists list --format json
```

```json
[
  {
    "collaborative": false,
    "description": "Car Music Mix 2022 🔥 Best Remixes of Popular Songs 2022 EDM, Bass Boosted  by Rise Music",
    "external_urls": {
      "spotify": "https://open.spotify.com/playlist/0fM4AkfoGygOHVXjsNB7io"
    }
  }
]
```

### Find duplicates across all playlists and display additional details

```text
spotify-utils playlists duplicates --verbose
```

**Output:**

```text
Found 43 duplicate tracks across 20 playlists

| Index | Name              | Artists                 | Playlists              | Track ID               |
|-------|-------------------|-------------------------|------------------------|------------------------|
| 0     | Piercing Light    | League of Legends, Mako | Rock, Sonos Mainstream | 0163ud7I4Vb0ID5K7WBkq9 |
| 1     | Edge Of The Earth | Thirty Seconds To Mars  | Rock, Pop              | 0g9IOJwdElaCZEvcqGRP4b |
| ...   | ...               | ...                     | ...                    | ...                    |
```

### Find removed or unavailable tracks across all playlists

```text
spotify-utils playlists unavailable --verbose
```

**Output:**

```text
Found 3 unavailable tracks across 20 playlists

| Index | Name            | Artists     | Playlist | Reason  |
|-------|-----------------|-------------|----------|---------|
| 0     | (removed track) |             | Rock     | removed |
| 1     | Some Song       | Some Artist | Pop      | market  |
| ...   | ...             | ...         | ...      | ...     |
```

### Export playlists as HTML

```text
spotify-utils playlists export --format html
```

![HTML export](https://raw.githubusercontent.com/fabieu/spotify-utils/main/docs/examples/html_export.png)

### Export specific playlist as JSON

```text
spotify-utils playlists export --format json --id {PLAYLIST_ID}
```

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.

## Disclaimer

> [!IMPORTANT]
> This project isn’t endorsed by Spotify AB and doesn’t reflect the views or opinions of Spotify AB or anyone officially
> involved in producing or managing Spotify&reg;
