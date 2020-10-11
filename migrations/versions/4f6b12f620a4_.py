"""empty message

Revision ID: 4f6b12f620a4
Revises: 43355600985b
Create Date: 2020-10-09 16:22:59.116717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f6b12f620a4'
down_revision = '43355600985b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('duration', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'duration')
    # ### end Alembic commands ###