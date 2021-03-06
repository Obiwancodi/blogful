"""empty message

Revision ID: 17b53dcb2f32
Revises: None
Create Date: 2015-01-23 19:01:08.233480

"""

# revision identifiers, used by Alembic.
revision = '17b53dcb2f32'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'posts', 'users', ['author_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_column('posts', 'author_id')
    ### end Alembic commands ###
