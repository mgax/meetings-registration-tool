"""Removed role from Staff model

Revision ID: c3d8dfe84e3
Revises: b34bd8c9b63
Create Date: 2014-08-04 16:37:08.647845

"""

# revision identifiers, used by Alembic.
revision = 'c3d8dfe84e3'
down_revision = 'b34bd8c9b63'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('staff', 'role_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('staff', sa.Column('role_id', sa.INTEGER(), autoincrement=False, nullable=False))
    ### end Alembic commands ###