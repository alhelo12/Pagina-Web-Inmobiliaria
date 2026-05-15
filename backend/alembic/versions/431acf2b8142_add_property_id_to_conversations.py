"""add_property_id_to_conversations

Revision ID: 431acf2b8142
Revises: 339664da3af1
Create Date: 2026-05-14 23:15:35.069008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '431acf2b8142'
down_revision: Union[str, None] = '339664da3af1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'conversations',
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('properties.id'), nullable=True)
    )
    op.create_index('ix_conversations_property_id', 'conversations', ['property_id'])


def downgrade() -> None:
    op.drop_index('ix_conversations_property_id', 'conversations')
    op.drop_column('conversations', 'property_id')
