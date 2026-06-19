"""add user_preferences to users

Revision ID: 0a1b2c3d4e5f
Revises: 9a8b7c6d5e4f
Create Date: 2026-06-19 16:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0a1b2c3d4e5f'
down_revision: Union[str, None] = '9a8b7c6d5e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',
        sa.Column(
            'user_preferences',
            sa.JSON(),
            server_default=sa.text("'{\"all\": true}'::json"),
            comment="Preferencias de notificación del usuario (JSON)"
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'user_preferences')