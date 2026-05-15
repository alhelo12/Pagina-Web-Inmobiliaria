"""add full text search to properties

Revision ID: 846f1b9184c5
Revises: 2e15e28e5a25
Create Date: 2026-05-14 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '846f1b9184c5'
down_revision: Union[str, None] = '2e15e28e5a25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE properties ADD COLUMN search_vector tsvector
            GENERATED ALWAYS AS (
                setweight(to_tsvector('spanish', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('spanish', coalesce(description, '')), 'B') ||
                setweight(to_tsvector('spanish', coalesce(city, '')), 'C') ||
                setweight(to_tsvector('spanish', coalesce(property_type, '')), 'D')
            ) STORED
    """)

    op.execute("""
        CREATE INDEX idx_properties_search_vector ON properties USING GIN(search_vector)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_properties_search_vector")
    op.execute("ALTER TABLE properties DROP COLUMN IF EXISTS search_vector")
