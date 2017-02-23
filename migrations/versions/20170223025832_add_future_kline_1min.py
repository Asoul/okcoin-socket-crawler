"""Add future kline 1min

Revision ID: 9c2dcdde9
Revises: 2de5270e1c3
Create Date: 2017-02-23 02:58:32.227072

"""

# revision identifiers, used by Alembic.
revision = '9c2dcdde9'
down_revision = '2de5270e1c3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'future_kline_1min',
        sa.Column('timestamp', sa.Integer, primary_key=True),
        sa.Column('open', sa.Float, nullable=False),
        sa.Column('high', sa.Float, nullable=False),
        sa.Column('low', sa.Float, nullable=False),
        sa.Column('close', sa.Float, nullable=False),
        sa.Column('volume', sa.Integer, nullable=False),
        sa.Column('volume_btc', sa.Float, nullable=False)
    )

def downgrade():
    op.drop_table('future_kline_1min')
