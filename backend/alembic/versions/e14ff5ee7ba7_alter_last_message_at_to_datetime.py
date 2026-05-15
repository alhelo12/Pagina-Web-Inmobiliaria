"""alter_last_message_at_to_datetime

Revision ID: e14ff5ee7ba7
Revises: 7cabdad1336a
Create Date: 2026-05-14 23:15:22.044140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e14ff5ee7ba7'
down_revision: Union[str, None] = '7cabdad1336a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'conversations',
        'last_message_at',
        existing_type=sa.String(30),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using='last_message_at::timestamp'
    )


def downgrade() -> None:
    op.alter_column(
        'conversations',
        'last_message_at',
        existing_type=sa.DateTime(),
        type_=sa.String(30),
        existing_nullable=True
    )
