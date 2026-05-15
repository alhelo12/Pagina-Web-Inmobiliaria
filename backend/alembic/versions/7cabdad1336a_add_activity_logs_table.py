"""add activity_logs table

Revision ID: 7cabdad1336a
Revises: 846f1b9184c5
Create Date: 2026-05-14 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7cabdad1336a'
down_revision: Union[str, None] = '846f1b9184c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False, index=True),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.Integer, nullable=True),
        sa.Column('details', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('activity_logs')
