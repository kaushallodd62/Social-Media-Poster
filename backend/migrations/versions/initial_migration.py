"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-03-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('profile_picture', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('verification_token', sa.String(length=100), nullable=True),
        sa.Column('reset_password_token', sa.String(length=100), nullable=True),
        sa.Column('reset_password_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('verification_token'),
        sa.UniqueConstraint('reset_password_token')
    )

    # Create oauth_credentials table
    op.create_table('oauth_credentials',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(length=50), server_default='Bearer', nullable=True),
        sa.Column('id_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_user_provider')
    )

    # Create media_items table
    op.create_table('media_items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('google_media_id', sa.String(length=255), nullable=False),
        sa.Column('base_url', sa.Text(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=True),
        sa.Column('mime_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('creation_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('exif_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags_json', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'google_media_id', name='uq_user_media')
    )

    # Create ranking_sessions table
    op.create_table('ranking_sessions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('method', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create media_rankings table
    op.create_table('media_rankings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('ranking_session_id', sa.BigInteger(), nullable=False),
        sa.Column('media_item_id', sa.BigInteger(), nullable=False),
        sa.Column('technical_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('aesthetic_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('combined_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('llm_reasoning', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags_json', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['media_item_id'], ['media_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ranking_session_id'], ['ranking_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on media_rankings
    op.create_index('idx_media_rankings_session_score', 'media_rankings', ['ranking_session_id', 'combined_score'])

def downgrade() -> None:
    op.drop_index('idx_media_rankings_session_score', table_name='media_rankings')
    op.drop_table('media_rankings')
    op.drop_table('ranking_sessions')
    op.drop_table('media_items')
    op.drop_table('oauth_credentials')
    op.drop_table('users') 