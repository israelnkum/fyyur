"""Added missing fields to Venue Model

Revision ID: 341da17a89e9
Revises: b83884f75469
Create Date: 2022-08-12 11:54:04.371978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '341da17a89e9'
down_revision = 'b83884f75469'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue__genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('genre', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('Venue', sa.Column('website_link', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=255), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), server_default='false', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'website_link')
    op.drop_table('venue__genre')
    # ### end Alembic commands ###
