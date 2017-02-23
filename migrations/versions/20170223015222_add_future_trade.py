"""Add future_trade

Revision ID: 2de5270e1c3
Revises: 4392dba5b4c
Create Date: 2017-02-23 01:52:22.585482

"""

# revision identifiers, used by Alembic.
revision = '2de5270e1c3'
down_revision = '4392dba5b4c'

from alembic import op
import sqlalchemy as sa
import enum

def upgrade():
    op.create_table(
        'future_trade',
        sa.Column('trade_id', sa.BigInteger, primary_key=True),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('timestamp', sa.Integer, nullable=False),
        sa.Column('trade_type', sa.SmallInteger, nullable=False),
        sa.Column('contract_type', sa.SmallInteger, nullable=False),
    )

    op.create_index('future_trade_timestamp_index', 'future_trade', ['timestamp'])

def downgrade():
    op.drop_table('future_trade')
