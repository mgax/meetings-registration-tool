"""Added representing field on category

Revision ID: 1b47bf052703
Revises: 4bc86157e7bf
Create Date: 2014-09-05 10:57:23.146960

"""

# revision identifiers, used by Alembic.
revision = '1b47bf052703'
down_revision = '4bc86157e7bf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('representing',
                  sa.String(length=128), nullable=True))
    op.add_column('category_default', sa.Column('representing',
                  sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('category_default', 'representing')
    op.drop_column('category', 'representing')
    ### end Alembic commands ###