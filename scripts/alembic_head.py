"""Resolve the repository's single official Alembic head from its revision graph."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT_LOCATION = REPOSITORY_ROOT / "apps" / "api" / "migrations"


def official_alembic_head(script_location: Path = DEFAULT_SCRIPT_LOCATION) -> str:
    config = Config()
    config.set_main_option("script_location", str(script_location.resolve()))
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected exactly one Alembic head, found {len(heads)}")
    return heads[0]
