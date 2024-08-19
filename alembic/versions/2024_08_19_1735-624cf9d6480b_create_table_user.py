"""create table user

Revision ID: 624cf9d6480b
Revises: 
Create Date: 2024-08-19 17:35:27.062752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '624cf9d6480b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lebedev_user',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.Column('balance', sa.BigInteger(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('verification_vector', sa.ARRAY(sa.Numeric(precision=8, scale=7)), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lebedev_user')
    # ### end Alembic commands ###