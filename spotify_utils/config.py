from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="SPOTIFY_UTILS",
    settings_files=['settings.toml', '.secrets.toml'],
    load_dotenv=True,
    validators=[
        # Ensure some parameters exists (are required)
        Validator('CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI', must_exist=True),
        Validator('CACHE', default=None),
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
