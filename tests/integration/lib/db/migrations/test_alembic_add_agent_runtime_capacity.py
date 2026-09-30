"""Alembic schema migration: Agent 凭证持久化显式运行容量。"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import sqlalchemy as sa
from alembic.config import Config

from alembic import command


def test_upgrade_adds_nullable_agent_runtime_capacity(
    alembic_cfg: tuple[Config, Path], migration_revisions: Callable[[str], tuple[str, str]]
) -> None:
    revision, parent = migration_revisions("*_add_agent_runtime_capacity.py")
    cfg, db_path = alembic_cfg
    command.upgrade(cfg, parent)

    engine = sa.create_engine(f"sqlite:///{db_path}")
    try:
        command.upgrade(cfg, revision)
        columns = {column["name"]: column for column in sa.inspect(engine).get_columns("agent_anthropic_credentials")}
    finally:
        engine.dispose()

    for name in ("context_window_tokens", "auto_compact_window_tokens", "max_output_tokens"):
        assert name in columns
        assert columns[name]["nullable"] is True
