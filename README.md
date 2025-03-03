<div id="top"></div>
<!-- PROJECT SHIELDS -->

![PyPI](https://img.shields.io/pypi/v/spotify-utils?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spotify-utils?style=for-the-badge)
[![GitHub pipeline status](https://img.shields.io/github/actions/workflow/status/fabieu/spotify-utils/build.yml?style=for-the-badge)](https://github.com/fabieu/spotify-utils/actions)
[![GitHub issues](https://img.shields.io/github/issues-raw/fabieu/spotify-utils?style=for-the-badge)](https://github.com/fabieu/spotify-utils/issues)
[![GitHub merge requests](https://img.shields.io/github/issues-pr/fabieu/spotify-utils?style=for-the-badge)](https://github.com/fabieu/spotify-utils/pulls)
[![GitHub](https://img.shields.io/github/license/fabieu/spotify-utils?style=for-the-badge)](https://github.com/fabieu/spotify-utils/blob/main/LICENSE)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/fabieu/spotify-utils">
    <img src="https://raw.githubusercontent.com/fabieu/spotify-utils/main/docs/logo.svg" alt="Logo" width="200" height="200">
  </a>

<h2 align="center">spotify-utils</h2>

  <p align="center">
    An awesome and easy-to-use CLI for various Spotify&reg; utility tasks!
    <br />
    <a href=https://github.com/fabieu/spotify-utils/-/issues">Report Bug</a>
    ·
    <a href="https://github.com/fabieu/spotify-utils/-/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

There are many Spotify&reg; clients out there; however, I didn't find one that really suited my needs so I created this
one. I want to create a Spotify&reg; CLI which is easy-to-use, packed with useful functionalities and with a
sophisticated documentation built-in.

Key features:

- Playlists
    - List information about playlists of the authenticated user in various output formats (Console, JSON)
    - Find duplicate tracks across all playlists
    - Export playlist information in various formats (JSON, HTML template)
- More coming soon

Of course, this CLI will not serve all needs, especially during development. So I'll be adding more features in the near
future. You may also suggest changes by forking this repo and creating a pull request or opening an issue. Thanks to all
the people have contributed!

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation

```bash
pip install spotify-utils
```

### Configuration

All methods require user authorization. You will need to register your app
at [My Dashboard](https://developer.spotify.com/dashboard/applications) to get the credentials necessary to make
authorized calls (a client id and client
secret). [Click here](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/) to go to
the step-by-step guide for creating a Spotify&reg; application.

The CLI uses the Authorization Code flow, which the user logs into once. It provides an access token that can be
refreshed.

Environment variables are being used for configuration. In order for the CLI to function properly you need to provide
the following environment variables (use export instead of SET on Linux):

```powershell
set SPOTIFY_UTILS_CLIENT_ID='your-spotify-client-id'
set SPOTIFY_UTILS_CLIENT_SECRET='your-spotify-client-secret'
set SPOTIFY_UTILS_REDIRECT_URI='your-app-redirect-url'
```

In addition the use of an `.env` file is supported:

```
SPOTIFY_UTILS_CLIENT_ID='your-spotify-client-id'
SPOTIFY_UTILS_CLIENT_SECRET='your-spotify-client-secret'
SPOTIFY_UTILS_REDIRECT_URI='your-app-redirect-url'
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage and examples

In this section you can find usage examples of the CLI

### List all playlists of the current authenticated user in JSON format

```text
spotify-utils playlists list --json
```

```json
[
  {
    "collaborative": false,
    "description": "Car Music Mix 2022 \ud83d\udd25 Best Remixes of Popular Songs 2022 EDM, Bass Boosted  by Rise Music",
    "external_urls": {
      "spotify": "https://open.spotify.com/playlist/0fM4AkfoGygOHVXjsNB7io"
    },
    ... more
  }
]
```

### Find duplicates across all playlists and display additional details:

```text
spotify-utils playlists duplicates --verbose
```

Found 43 duplicate tracks across 20 playlists
| Index | Name | Artists | Playlists | Track ID |
| --- | --- | --- | --- | --- |
| 0 | Piercing Light | League of Legends, Mako | Rock, Sonos Mainstream | 0163ud7I4Vb0ID5K7WBkq9 |
| 1 | Edge Of The Earth | Thirty Seconds To Mars | Rock, Pop | 0g9IOJwdElaCZEvcqGRP4b |
| ... | ... | ... | ... | ... |

### Export playlist as beautiful HTML file

```text
spotify-utils playlists export --html
```

![HTML export](https://raw.githubusercontent.com/fabieu/spotify-utils/main/docs/examples/html_export.png)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [ ] Improve help sections of the CLI
- [ ] Add additional functionality

See the [open issues](https://github.com/fabieu/spotify-utils/-/issues) for a full list of proposed features (and known
issues).

<p align="right">(<a href="#top">back to top</a>)</p>

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

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

- [Typer](https://github.com/tiangolo/typer)
- [Spotipy](https://github.com/plamere/spotipy)
- [Vermin](https://github.com/netromdk/vermin)
- [Shields.io](https://shields.io)
- [Choose an Open Source License](https://choosealicense.com)

<p align="right">(<a href="#top">back to top</a>)</p>

## Disclaimer

This project isn’t endorsed by Spotify AB and doesn’t reflect the views or opinions of Spotify AB or anyone officially
involved in producing or managing Spotify&reg;

<p align="right">(<a href="#top">back to top</a>)</p>
