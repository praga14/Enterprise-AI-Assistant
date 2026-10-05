"""add embeddings to document chunks

Revision ID: bb7357a7de87
Revises: 0f2d919a950d
Create Date: 2026-09-23 10:58:12.168072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'bb7357a7de87'
down_revision: Union[str, Sequence[str], None] = '0f2d919a950d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'document_chunks',
        sa.Column(
            'embedding',
            Vector(dim=384),
            nullable=True,
        ),
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('document_chunks', 'embedding')