"""Add future_index

Revision ID: 4392dba5b4c
Revises: None
Create Date: 2017-02-23 00:34:16.236987

"""

# revision identifiers, used by Alembic.
revision = '4392dba5b4c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'future_index',
        sa.Column('timestamp', sa.BigInteger, primary_key=True),
        sa.Column('value', sa.Float, nullable=False)
    )

def downgrade():
    op.drop_table('future_index')
