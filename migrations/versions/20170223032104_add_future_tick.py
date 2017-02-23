"""Add future tick

Revision ID: 469de48f7bd
Revises: 9c2dcdde9
Create Date: 2017-02-23 03:21:04.723851

"""

# revision identifiers, used by Alembic.
revision = '469de48f7bd'
down_revision = '9c2dcdde9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'future_tick',
        sa.Column('timestamp', sa.BigInteger, primary_key=True),
        sa.Column('low', sa.Float, nullable=False),
        sa.Column('buy', sa.Float, nullable=False),
        sa.Column('last', sa.Float, nullable=False),
        sa.Column('sell', sa.Float, nullable=False),
        sa.Column('high', sa.Float, nullable=False),
        sa.Column('volume', sa.Integer, nullable=False)
    )

def downgrade():
    op.drop_table('future_tick')
