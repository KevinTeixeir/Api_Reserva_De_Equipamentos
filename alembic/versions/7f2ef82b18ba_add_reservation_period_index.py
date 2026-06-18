"""add reservation period index

Revision ID: 7f2ef82b18ba
Revises: e2e4ebbf4703
Create Date: 2026-06-16 00:26:30.005356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f2ef82b18ba'
down_revision: Union[str, Sequence[str], None] = 'e2e4ebbf4703'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_reservation_period",
        "reservations",
        [
            "equipment_id",
            "start_date",
            "end_date",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_reservation_period",
        table_name="reservations",
    )