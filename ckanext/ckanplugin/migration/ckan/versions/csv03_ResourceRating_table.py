"""create ResourceRating tables

Revision ID: 3b4894672727
Revises:
Create Date: 2023-11-02 15:53:02.262586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "csv03"
down_revision = "csv02"
branch_labels = None
depends_on = None


def upgrade():
    engine = op.get_bind()
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    if "ResourceRating" not in tables:
        op.create_table(
            "ResourceRating",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("package_Id", sa.UnicodeText, sa.ForeignKey('package.id',ondelete='CASCADE')),
            sa.Column("ratings", sa.Integer, default=0),
            sa.Column("user_id", sa.UnicodeText),            
            sa.Column("created", sa.DateTime, default=sa.func.now()           
            ),
        )
    


def downgrade():
    op.drop_table("contadores")