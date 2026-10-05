"""add system protection to roles and permissions

Revision ID: a4bd2ac12dae
Revises: 44c94442d4aa
Create Date: 2026-09-22 14:19:16.507870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4bd2ac12dae"
down_revision: Union[str, Sequence[str], None] = "44c94442d4aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "permissions",
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "roles",
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("roles", "is_system")
    op.drop_column("permissions", "is_system")