"""empty message

Revision ID: 743797c92cf1
Revises: db02590be7d2
Create Date: 2020-10-11 09:37:16.747959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '743797c92cf1'
down_revision = 'db02590be7d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('artist_id', sa.Integer(), nullable=True))
    op.drop_constraint('album_artist_fkey', 'album', type_='foreignkey')
    op.create_foreign_key(None, 'album', 'artist', ['artist_id'], ['id'])
    op.drop_column('album', 'artist')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('artist', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'album', type_='foreignkey')
    op.create_foreign_key('album_artist_fkey', 'album', 'artist', ['artist'], ['id'])
    op.drop_column('album', 'artist_id')
    # ### end Alembic commands ###
