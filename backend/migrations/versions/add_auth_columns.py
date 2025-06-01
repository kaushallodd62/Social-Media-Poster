"""Add authentication columns to users table

Revision ID: add_auth_columns
Revises: initial_migration
Create Date: 2024-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_auth_columns'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add authentication-related columns to users table
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_password_token', sa.String(length=255), nullable=True))

def downgrade() -> None:
    # Remove authentication-related columns from users table
    op.drop_column('users', 'reset_password_token')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'password_hash') 