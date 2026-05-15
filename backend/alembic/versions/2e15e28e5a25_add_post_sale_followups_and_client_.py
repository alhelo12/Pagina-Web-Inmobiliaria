"""add post_sale_followups and client_advisor_assignments

Revision ID: 2e15e28e5a25
Revises: 605c1a6623a9
Create Date: 2026-05-14 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '2e15e28e5a25'
down_revision: Union[str, None] = '605c1a6623a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'post_sale_followups',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('property_id', sa.Integer, sa.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('advisor_id', sa.Integer, sa.ForeignKey('advisors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sale_date', sa.TIMESTAMP, nullable=False),
        sa.Column('followup_type', sa.String(50), nullable=False, index=True),
        sa.Column('scheduled_date', sa.TIMESTAMP, nullable=False, index=True),
        sa.Column('completed_date', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(50), default='pending', index=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('satisfaction_score', sa.SmallInteger, sa.CheckConstraint('satisfaction_score BETWEEN 1 AND 5'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=False),
    )

    op.create_table(
        'client_advisor_assignments',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('advisor_id', sa.Integer, sa.ForeignKey('advisors.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('assigned_date', sa.TIMESTAMP, nullable=False),
        sa.Column('end_date', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(50), default='active', index=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('client_advisor_assignments')
    op.drop_table('post_sale_followups')
