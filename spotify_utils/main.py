try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Built-in modules
import importlib.metadata

# PyPi modules
import typer

# Local modules
from spotify_utils.src import playlists

# Global variables
__version__ = importlib.metadata.version("spotify-utils")

# Initialize Typer and populate commands
app = typer.Typer(help=f"spotify-utils: Version {__version__}")
app.add_typer(playlists.app, name="playlists")

if __name__ == "__main__":
    app()
