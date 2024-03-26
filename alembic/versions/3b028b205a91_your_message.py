"""your message

Revision ID: 3b028b205a91
Revises: 
Create Date: 2024-03-21 23:27:35.124768

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b028b205a91"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "traders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=True),
        sa.Column("api_secret", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_traders_email"), "traders", ["email"], unique=True)
    op.create_table(
        "followers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=True),
        sa.Column("api_secret", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("trader_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["trader_id"],
            ["traders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_followers_email"), "followers", ["email"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_followers_email"), table_name="followers")
    op.drop_table("followers")
    op.drop_index(op.f("ix_traders_email"), table_name="traders")
    op.drop_table("traders")
    # ### end Alembic commands ###