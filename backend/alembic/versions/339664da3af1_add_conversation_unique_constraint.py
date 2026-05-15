"""add_conversation_unique_constraint

Revision ID: 339664da3af1
Revises: e14ff5ee7ba7
Create Date: 2026-05-14 23:15:29.004682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '339664da3af1'
down_revision: Union[str, None] = 'e14ff5ee7ba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_conversation_user_advisor',
        'conversations',
        ['user_id', 'advisor_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_conversation_user_advisor',
        'conversations',
        type_='unique'
    )
