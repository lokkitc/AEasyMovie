"""create login attempts table

Revision ID: 2025_05_09_create_login_attempts
Revises: 71e25ebe032d
Create Date: 2025-05-09 22:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_05_09_create_login_attempts'
down_revision: Union[str, None] = '71e25ebe032d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_login_attempts_email_created_at',
        'login_attempts',
        ['email', 'created_at']
    )


def downgrade() -> None:
    op.drop_index('ix_login_attempts_email_created_at')
    op.drop_table('login_attempts') 