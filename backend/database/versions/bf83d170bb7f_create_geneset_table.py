"""create_geneset_table

Revision ID: bf83d170bb7f
Revises: 5a363594dd06
Create Date: 2021-02-22 20:32:01.329837

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
from sqlalchemy.dialects.postgresql import ENUM

revision = "bf83d170bb7f"
down_revision = "5a363594dd06"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "geneset",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("gene_symbols", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("collection_id", sa.String(), nullable=False),
        sa.Column(
            "collection_visibility",
            ENUM("PUBLIC", "PRIVATE", name="collectionvisibility", create_type=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["collection_id", "collection_visibility"],
            ["project.id", "project.visibility"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "collection_id", "collection_visibility", name="_geneset_name__collection_uc"),
    )
    op.create_table(
        "geneset_dataset_link",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("geneset_id", sa.String(), nullable=False),
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.id"],
        ),
        sa.ForeignKeyConstraint(
            ["geneset_id"],
            ["geneset.id"],
        ),
        sa.PrimaryKeyConstraint("id", "geneset_id", "dataset_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("geneset_dataset_link")
    op.drop_table("geneset")
    # ### end Alembic commands ###
