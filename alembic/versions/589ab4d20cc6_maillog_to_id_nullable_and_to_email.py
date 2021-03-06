"""MailLog to_id nullable and to_email

Revision ID: 589ab4d20cc6
Revises: a1645606de5
Create Date: 2015-05-29 17:18:07.923296

"""

# revision identifiers, used by Alembic.
revision = '589ab4d20cc6'
down_revision = 'a1645606de5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mail_log', sa.Column('to_email', sa.String(length=128),
                  nullable=True))
    op.alter_column('mail_log', 'to_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mail_log', 'to_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
    op.drop_column('mail_log', 'to_email')
    ### end Alembic commands ###
