"""setup_foreign_keys

Revision ID: bb7fd74216be
Revises: 407ab1d9843a
Create Date: 2020-02-04 14:51:37.477811

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bb7fd74216be"
down_revision = "407ab1d9843a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "library_prep_protocol_biosample_prep",
        "library_prep_protocol",
        "biosample_prep",
        ["biosample_prep_id"],
        ["id"],
    )

    op.create_foreign_key(
        "library_library_prep_protocol",
        "library",
        "library_prep_protocol",
        ["library_prep_protocol_id"],
        ["id"],
    )

    op.create_foreign_key(
        "library_sequencing_protocol",
        "library",
        "sequencing_protocol",
        ["sequencing_protocol_id"],
        ["id"],
    )

    op.create_foreign_key(
        "library_project", "library", "project", ["project_id"], ["id"]
    )

    op.create_foreign_key(
        "contributor_project", "contributor", "project", ["project_id"], ["id"]
    )

    op.create_foreign_key(
        "sequence_file_sequencing_protocol",
        "sequence_file",
        "sequencing_protocol",
        ["sequencing_protocol_id"],
        ["id"],
    )


def downgrade():
    pass
