"""create contadores tables

Revision ID: 3b4894672727
Revises:
Create Date: 2023-11-02 15:53:02.262586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "csv01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    engine = op.get_bind()
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    if "contadores" not in tables:
        op.create_table(
            "contadores",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("package_Id", sa.UnicodeText, sa.ForeignKey('package.id',ondelete='CASCADE')),
            sa.Column("source_Id", sa.UnicodeText, sa.ForeignKey('resource.id',ondelete='CASCADE')),
            sa.Column("contVistas", sa.Integer, default=0),
            sa.Column("contDownload", sa.Integer, default=0),            
            sa.Column("created", sa.DateTime, default=sa.func.now()           
            ),
        )
    


def downgrade():
    op.drop_table("contadores")
