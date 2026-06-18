import importlib.metadata
import sys

import typer

from spotify_utils.src import playlists
from spotify_utils.src.auth import AuthenticationError

# Global variables
__version__ = importlib.metadata.version("spotify-utils")

# Initialize Typer and populate commands
app = typer.Typer(help=f"spotify-utils v{__version__}")
app.add_typer(playlists.app, name="playlists")


@app.command()
def version():
    typer.echo(f"spotify-utils v{__version__}")


@app.command()
def tui():
    """Launch the interactive TUI."""
    from spotify_utils.src.tui.app import SpotifyUtilsApp
    SpotifyUtilsApp().run()


def main() -> None:
    """Console-script entry point: present auth failures cleanly instead of as a traceback."""
    try:
        app()
    except AuthenticationError as exc:
        typer.echo(str(exc), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
