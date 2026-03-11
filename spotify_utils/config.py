from pathlib import Path

from dynaconf import Dynaconf

_CONFIG_DIR = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="SPOTIFY_UTILS",
    root_path=str(_CONFIG_DIR),
    settings_files=['settings.toml', '.secrets.toml'],
)

_REQUIRED = ("CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI")


def settings_configured() -> bool:
    return all(settings.get(k) for k in _REQUIRED)


def write_secrets(client_id: str, client_secret: str, redirect_uri: str) -> None:
    content = (
        f'CLIENT_ID = "{client_id}"\n'
        f'CLIENT_SECRET = "{client_secret}"\n'
        f'REDIRECT_URI = "{redirect_uri}"\n'
    )
    (_CONFIG_DIR / ".secrets.toml").write_text(content, encoding="utf-8")
    settings.reload()
