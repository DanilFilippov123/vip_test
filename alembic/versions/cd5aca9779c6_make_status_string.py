"""Make status string

Revision ID: cd5aca9779c6
Revises: 63a070b47844
Create Date: 2024-05-06 21:21:39.426153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd5aca9779c6'
down_revision: Union[str, None] = '63a070b47844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensor_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('current_value_counter', sa.Integer(), nullable=True),
    sa.Column('pressure_value', sa.Float(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sensor_data')
    # ### end Alembic commands ###