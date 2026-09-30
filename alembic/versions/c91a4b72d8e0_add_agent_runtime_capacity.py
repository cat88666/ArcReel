"""Agent 凭证增加显式运行容量

Revision ID: c91a4b72d8e0
Revises: d7e4a2c95b10
Create Date: 2026-09-29 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c91a4b72d8e0"
down_revision: str | Sequence[str] | None = "d7e4a2c95b10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("agent_anthropic_credentials") as batch_op:
        batch_op.add_column(sa.Column("context_window_tokens", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("auto_compact_window_tokens", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("max_output_tokens", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("agent_anthropic_credentials") as batch_op:
        batch_op.drop_column("max_output_tokens")
        batch_op.drop_column("auto_compact_window_tokens")
        batch_op.drop_column("context_window_tokens")
