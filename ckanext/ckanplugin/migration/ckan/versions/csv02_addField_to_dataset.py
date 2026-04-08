"""Add Field Table Dataset

Revision ID: 3b4894672727
Revises:
Create Date: 2026-02-24 15:53:02.262586

"""
from alembic import op
import sqlalchemy as sa
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = "csv02"
down_revision = "csv01"
branch_labels = None
depends_on = None

table = 'package'

def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    op.add_column(table, sa.Column('city', sa.UnicodeText))
    op.add_column(table, sa.Column('department', sa.UnicodeText))
    op.add_column(table, sa.Column('update_frequency', sa.UnicodeText))


def downgrade():
    op.drop_column(table, 'city')
    op.drop_column(table, 'department')
    op.drop_column(table, 'update_frequency')