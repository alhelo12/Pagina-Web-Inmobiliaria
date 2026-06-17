"""add is_email_verified to users

Revision ID: 9a8b7c6d5e4f
Revises: 3643a157ea4e
Create Date: 2026-06-17 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a8b7c6d5e4f'
down_revision: Union[str, None] = '3643a157ea4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # Existing users are considered verified
    op.execute("UPDATE users SET is_email_verified = TRUE")


def downgrade() -> None:
    op.drop_column('users', 'is_email_verified')
