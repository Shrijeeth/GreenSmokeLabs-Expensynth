"""create-transaction-model

Revision ID: 8f073d143810
Revises:
Create Date: 2025-06-04 15:15:33.935989

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f073d143810"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transaction_type", sa.String(), nullable=True),
        sa.Column("amount", sa.Numeric(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("third_party", sa.String(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transactions")
