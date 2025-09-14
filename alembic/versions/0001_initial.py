"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-12 00:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'games',
        sa.Column('appid', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('appid')
    )

    op.create_table(
        'achievements_global',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('appid', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('percent', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appid', 'name', name='uq_achievements_global_appid_name')
    )
    op.create_index('ix_achievements_global_appid', 'achievements_global', ['appid'])

    op.create_table(
        'ownerships',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('steamid', sa.String(length=32), nullable=False),
        sa.Column('appid', sa.Integer(), nullable=False),
        sa.Column('playtime_forever', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('steamid', 'appid', name='uq_ownerships_steamid_appid')
    )
    op.create_index('ix_ownerships_steamid', 'ownerships', ['steamid'])
    op.create_index('ix_ownerships_appid', 'ownerships', ['appid'])


def downgrade() -> None:
    op.drop_index('ix_ownerships_appid', table_name='ownerships')
    op.drop_index('ix_ownerships_steamid', table_name='ownerships')
    op.drop_table('ownerships')

    op.drop_index('ix_achievements_global_appid', table_name='achievements_global')
    op.drop_table('achievements_global')

    op.drop_table('games')
