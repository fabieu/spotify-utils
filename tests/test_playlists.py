import json
from datetime import date
from pathlib import Path

from spotify_utils.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_list():
    result = runner.invoke(app, ["playlists", "list"])
    assert result.exit_code == 0


def test_list_json():
    result = runner.invoke(app, ["playlists", "list", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) != None


def test_duplicates():
    result = runner.invoke(app, ["playlists", "duplicates"])
    assert result.exit_code == 0
    assert result.stdout != None


def test_duplicates_quiet():
    result = runner.invoke(app, ["playlists", "duplicates", "--quiet"])
    assert result.exit_code == 0
    assert len(result.stdout) == 0


def test_export_json():
    try:
        result = runner.invoke(app, ["playlists", "export", "--json", "--no-launch"])
        assert result.exit_code == 0

        # Check if file hase been created
        path = Path().cwd()
        outpath = path / f"playlist_export_{date.today()}.json"
        assert outpath.exists()

        # Test if file content is valid JSON
        with open(outpath) as f:
            assert json.load(f) != None
    finally:
        outpath.unlink()


def test_export_html():
    try:
        result = runner.invoke(app, ["playlists", "export", "--html", "--no-launch"])
        print(result)
        assert result.exit_code == 0

        # Check if file hase been created and is not empty
        path = Path().cwd()
        outpath = path / f"playlist_export_{date.today()}.html"
        assert outpath.exists()
        assert outpath.stat().st_size != 0
    finally:
        outpath.unlink()
