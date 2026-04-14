"""backfill default pool group

Revision ID: eae5098b8737
Revises: c5256fd7a465
"""

from alembic import op
import sqlalchemy as sa

revision = "eae5098b8737"
down_revision = "c5256fd7a465"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # 1. Create default group
    conn.execute(sa.text("""
        INSERT INTO pool_group (name, slug, is_active, created_at, created_by_user_id)
        VALUES (:name, :slug, :is_active, NOW(), NULL)
        ON CONFLICT (slug) DO NOTHING
    """), {
        "name": "Main Pool",
        "slug": "main-pool",
        "is_active": True,
    })

    # 2. Add all users to group
    conn.execute(sa.text("""
        INSERT INTO group_member (group_id, user_id, role, is_active, joined_at)
        SELECT pg.id, u.id, 'member', TRUE, NOW()
        FROM pool_group pg
        CROSS JOIN "user" u
        WHERE pg.slug = :slug
          AND NOT EXISTS (
              SELECT 1 FROM group_member gm
              WHERE gm.group_id = pg.id AND gm.user_id = u.id
          )
    """), {
        "slug": "main-pool",
    })

    # 3. Backfill picks
    conn.execute(sa.text("""
        UPDATE pick
        SET group_id = pg.id
        FROM pool_group pg
        WHERE pg.slug = :slug
          AND pick.group_id IS NULL
    """), {
        "slug": "main-pool",
    })


def downgrade():
    conn = op.get_bind()

    conn.execute(sa.text("""
        UPDATE pick
        SET group_id = NULL
        WHERE group_id = (
            SELECT id FROM pool_group WHERE slug = :slug
        )
    """), {"slug": "main-pool"})

    conn.execute(sa.text("""
        DELETE FROM group_member
        WHERE group_id = (
            SELECT id FROM pool_group WHERE slug = :slug
        )
    """), {"slug": "main-pool"})

    conn.execute(sa.text("""
        DELETE FROM pool_group
        WHERE slug = :slug
    """), {"slug": "main-pool"})