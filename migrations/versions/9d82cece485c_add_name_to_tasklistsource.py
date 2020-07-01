"""Add name to TasklistSource

Revision ID: 9d82cece485c
Revises: 0e1a1bc56a6c
Create Date: 2020-07-01 17:07:47.136180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d82cece485c'
down_revision = '0e1a1bc56a6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasklist_source', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasklist_source', 'name')
    # ### end Alembic commands ###