"""align notification preferences schema

Revision ID: 682994230f39
Revises: 1751639a973d
Create Date: 2026-07-16 00:20:27.409193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '682994230f39'
down_revision: Union[str, None] = '1751639a973d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('DROP TABLE IF EXISTS notification_preferences')
    op.alter_column('users', 'is_email_verified',
               existing_type=sa.BOOLEAN(),
               comment='Si el email del usuario ha sido verificado',
               existing_nullable=False,
               existing_server_default=sa.text('false'))


def downgrade() -> None:
    op.alter_column('users', 'is_email_verified',
               existing_type=sa.BOOLEAN(),
               comment=None,
               existing_comment='Si el email del usuario ha sido verificado',
               existing_nullable=False,
               existing_server_default=sa.text('false'))
    op.create_table('notification_preferences',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('enabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='notification_preferences_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='notification_preferences_pkey'),
    sa.UniqueConstraint('user_id', 'type', name='uq_user_notification_type', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_notification_preferences_id', 'notification_preferences', ['id'], unique=False)
