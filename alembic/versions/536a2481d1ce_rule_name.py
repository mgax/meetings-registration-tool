"""Rule name

Revision ID: 536a2481d1ce
Revises: 14b482ad5574
Create Date: 2015-01-22 15:42:52.701792

"""

# revision identifiers, used by Alembic.
revision = '536a2481d1ce'
down_revision = '14b482ad5574'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rule', sa.Column('name', sa.String(length=64), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rule', 'name')
    ### end Alembic commands ###
