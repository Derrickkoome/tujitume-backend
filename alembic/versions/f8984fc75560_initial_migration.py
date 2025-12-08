"""initial migration

Revision ID: f8984fc75560
Revises: 
Create Date: 2025-12-07 16:35:35.341159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8984fc75560'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
    sa.Column('uid', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('skills', sa.JSON(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_uid'), 'users', ['uid'], unique=False)
    
    # Create gigs table
    op.create_table('gigs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('budget', sa.Float(), nullable=True),
    sa.Column('budget_type', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('skills_required', sa.JSON(), nullable=True),
    sa.Column('deadline', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gigs_created_at'), 'gigs', ['created_at'], unique=False)
    op.create_index(op.f('ix_gigs_id'), 'gigs', ['id'], unique=False)
    op.create_index(op.f('ix_gigs_title'), 'gigs', ['title'], unique=False)
    
    # Create applications table
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gig_id', sa.Integer(), nullable=False),
    sa.Column('applicant_id', sa.String(), nullable=False),
    sa.Column('cover_letter', sa.Text(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['applicant_id'], ['users.uid'], ),
    sa.ForeignKeyConstraint(['gig_id'], ['gigs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')
    op.drop_index(op.f('ix_gigs_title'), table_name='gigs')
    op.drop_index(op.f('ix_gigs_id'), table_name='gigs')
    op.drop_index(op.f('ix_gigs_created_at'), table_name='gigs')
    op.drop_table('gigs')
    op.drop_index(op.f('ix_users_uid'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
