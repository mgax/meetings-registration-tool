"""unique constraints for rules and fields

Revision ID: 41cc4d896b41
Revises: 536a2481d1ce
Create Date: 2015-02-02 17:45:53.998891

"""

# revision identifiers, used by Alembic.
revision = '41cc4d896b41'
down_revision = '536a2481d1ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'action', ['field_id', 'rule_id'])
    op.create_unique_constraint(None, 'condition', ['field_id', 'rule_id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'condition', type_='unique')
    op.drop_constraint(None, 'action', type_='unique')
    ### end Alembic commands ###