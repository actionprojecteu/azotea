"""migrando BD antigua al nuevo SQLAlchemy ORM

Revision ID: 5ac5a963d667
Revises: 2d90c82cffb2
Create Date: 2026-10-20 13:04:20.798581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '5ac5a963d667'
down_revision: Union[str, Sequence[str], None] = '2d90c82cffb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def _count_invalid(bind, sql: str) -> int:
    return bind.execute(text(sql)).scalar_one()


def _require_zero(bind, sql: str, message: str) -> None:
    invalid = _count_invalid(bind, sql)
    if invalid:
        raise RuntimeError(f"{message}: {invalid} fila(s) inválida(s). Corrige los datos antes de migrar.")

def _require_no_foreign_key_violations(bind) -> None:
    violations = bind.execute(text("PRAGMA foreign_key_check")).fetchall()
    if violations:
        raise RuntimeError(
            f"La base contiene {len(violations)} violación(es) de claves ajenas: {violations[:10]}"
        )

def _validate_legacy_data(bind) -> None:
    _require_zero(
        bind,
        """
        SELECT COUNT(*) FROM camera_t
        WHERE bias IS NULL OR extension IS NULL OR header_type IS NULL
           OR bayer_pattern IS NULL OR width IS NULL OR length IS NULL
        """,
        "camera_t contiene valores NULL no permitidos en el esquema V3",
    )

    _require_zero(
        bind,
        """
        SELECT COUNT(*) FROM image_t
        WHERE hash IS NULL OR exptime IS NULL OR imagetype IS NULL OR flagged IS NULL
        """,
        "image_t contiene valores NULL no permitidos en el esquema V3",
    )

    _require_zero(
        bind,
        """
        SELECT COUNT(*) FROM sky_brightness_t
        WHERE aver_signal_R IS NULL OR vari_signal_R IS NULL
           OR aver_signal_G1 IS NULL OR vari_signal_G1 IS NULL
           OR aver_signal_G2 IS NULL OR vari_signal_G2 IS NULL
           OR aver_signal_B IS NULL OR vari_signal_B IS NULL
           OR published IS NULL
        """,
        "sky_brightness_t contiene valores NULL no permitidos en el esquema V3",
    )

    _require_zero(
        bind,
        "PRAGMA foreign_key_check",
        "La base contiene violaciones de claves ajenas",
    )



def upgrade() -> None:
    """Rebuild AZOTEA legacy tables to the V3 schema, preserving data."""

    bind = op.get_bind()
    _validate_legacy_data(bind)
    _require_no_foreign_key_violations(bind)

    # La vista depende de sky_brightness_t y roi_t: eliminarla antes.
    op.execute("DROP VIEW IF EXISTS sky_brightness_v")

    # 1) Renombrar tablas antiguas
    for table in (
        "sky_brightness_t",
        "image_t",
        "camera_t",
        "time_t",
        "date_t",
        "observer_t",
        "location_t",
        "roi_t",
        "config_t",
    ):
        op.rename_table(table, f"{table}_old")

    # 2) Crear tablas V3
    op.create_table(
        "config_t",
        sa.Column("section", sa.Text(), nullable=False),
        sa.Column("property", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("section", "property"),
    )

    op.create_table(
        "date_t",
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("sql_date", sa.Text(), nullable=False),
        sa.Column("date", sa.Text(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("day_year", sa.Integer(), nullable=False),
        sa.Column("julian_day", sa.Float(), nullable=False),
        sa.Column("weekday", sa.Text(), nullable=False),
        sa.Column("weekday_abbr", sa.Text(), nullable=False),
        sa.Column("weekday_num", sa.Integer(), nullable=False),
        sa.Column("month_num", sa.Integer(), nullable=False),
        sa.Column("month", sa.Text(), nullable=False),
        sa.Column("month_abbr", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("date_id"),
    )

    op.create_table(
        "time_t",
        sa.Column("time_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.Text(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("second", sa.Integer(), nullable=False),
        sa.Column("day_fraction", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("time_id"),
    )

    op.create_table(
        "observer_t",
        sa.Column("observer_id", sa.Integer(), nullable=False),
        sa.Column("family_name", sa.Text(), nullable=False),
        sa.Column("surname", sa.Text(), nullable=False),
        sa.Column("affiliation", sa.Text(), nullable=True),
        sa.Column("acronym", sa.Text(), nullable=True),
        sa.Column("valid_since", sa.DateTime(), nullable=False),
        sa.Column("valid_until", sa.DateTime(), nullable=False),
        sa.Column("valid_state", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("observer_id"),
        sa.UniqueConstraint(
            "family_name", "surname", "affiliation", "acronym",
            "valid_since", "valid_until",
        ),
    )

    op.create_table(
        "location_t",
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("site_name", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("randomized", sa.Integer(), nullable=True),
        sa.Column("utc_offset", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("location_id"),
        sa.UniqueConstraint("site_name", "location"),
    )

    op.create_table(
        "camera_t",
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("bias", sa.Integer(), nullable=False),
        sa.Column("extension", sa.Text(), nullable=False),
        sa.Column("header_type", sa.Text(), nullable=False),
        sa.Column("bayer_pattern", sa.Text(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column("x_pixsize", sa.Float(), nullable=True),
        sa.Column("y_pixsize", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("camera_id"),
        sa.UniqueConstraint("model"),
    )

    op.create_table(
        "roi_t",
        sa.Column("roi_id", sa.Integer(), nullable=False),
        sa.Column("x1", sa.Integer(), nullable=False),
        sa.Column("y1", sa.Integer(), nullable=False),
        sa.Column("x2", sa.Integer(), nullable=False),
        sa.Column("y2", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("roi_id"),
        sa.UniqueConstraint("x1", "y1", "x2", "y2"),
        sa.UniqueConstraint("display_name"),
    )

    op.create_table(
        "image_t",
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("directory", sa.Text(), nullable=False),
        sa.Column("hash", sa.LargeBinary(), nullable=False),
        sa.Column("iso", sa.Integer(), nullable=True),
        sa.Column("gain", sa.Float(), nullable=True),
        sa.Column("exptime", sa.Float(), nullable=False),
        sa.Column("focal_length", sa.Float(), nullable=True),
        sa.Column("f_number", sa.Float(), nullable=True),
        sa.Column("imagetype", sa.Text(), nullable=False),
        sa.Column("flagged", sa.Integer(), nullable=False),
        sa.Column("session", sa.BigInteger(), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("time_id", sa.Integer(), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("observer_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["date_id"], ["date_t.date_id"]),
        sa.ForeignKeyConstraint(["time_id"], ["time_t.time_id"]),
        sa.ForeignKeyConstraint(["camera_id"], ["camera_t.camera_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["location_t.location_id"]),
        sa.ForeignKeyConstraint(["observer_id"], ["observer_t.observer_id"]),
        sa.PrimaryKeyConstraint("image_id"),
        sa.UniqueConstraint("hash"),
    )

    op.create_table(
        "sky_brightness_t",
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("roi_id", sa.Integer(), nullable=False),
        sa.Column("aver_signal_R", sa.Float(), nullable=False),
        sa.Column("vari_signal_R", sa.Float(), nullable=False),
        sa.Column("aver_signal_G1", sa.Float(), nullable=False),
        sa.Column("vari_signal_G1", sa.Float(), nullable=False),
        sa.Column("aver_signal_G2", sa.Float(), nullable=False),
        sa.Column("vari_signal_G2", sa.Float(), nullable=False),
        sa.Column("aver_signal_B", sa.Float(), nullable=False),
        sa.Column("vari_signal_B", sa.Float(), nullable=False),
        sa.Column("published", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["image_t.image_id"]),
        sa.ForeignKeyConstraint(["roi_id"], ["roi_t.roi_id"]),
        sa.PrimaryKeyConstraint("image_id", "roi_id"),
    )

    # 3) Copiar datos. El orden de columnas coincide con el DDL antiguo.
    op.execute("INSERT INTO config_t SELECT * FROM config_old_t")
    op.execute("INSERT INTO date_t SELECT * FROM date_old_t")
    op.execute("INSERT INTO time_t SELECT * FROM time_old_t")
    op.execute("INSERT INTO observer_t SELECT * FROM observer_old_t")
    op.execute("INSERT INTO location_t SELECT * FROM location_old_t")
    op.execute("INSERT INTO camera_t SELECT * FROM camera_old_t")
    op.execute("INSERT INTO roi_t SELECT * FROM roi_old_t")
    op.execute("INSERT INTO image_t SELECT * FROM image_old_t")
    op.execute("INSERT INTO sky_brightness_t SELECT * FROM sky_brightness_old_t")

    # 4) Recrear la vista sobre las tablas V3
    op.execute("""
        CREATE VIEW sky_brightness_v AS
        SELECT
            s.image_id,
            r.x1,
            r.y1,
            r.x2,
            r.y2,
            r.display_name,
            r.comment,
            s.aver_signal_R,
            s.vari_signal_R,
            s.aver_signal_G1,
            s.vari_signal_G1,
            s.aver_signal_G2,
            s.vari_signal_G2,
            s.aver_signal_B,
            s.vari_signal_B,
            s.published,
            (r.y2 - r.y1) AS height,
            (r.x2 - r.x1) AS width
        FROM sky_brightness_t AS s
        JOIN roi_t AS r USING (roi_id)
    """)

    # 5) Borrar las tablas antiguas, primero las hijas
    op.drop_table("sky_brightness_old_t")
    op.drop_table("image_old_t")
    op.drop_table("camera_old_t")
    op.drop_table("time_old_t")
    op.drop_table("date_old_t")
    op.drop_table("observer_old_t")
    op.drop_table("location_old_t")
    op.drop_table("roi_old_t")
    op.drop_table("config_old_t")


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roi_t',
    sa.Column('roi_id', sa.INTEGER(), nullable=True),
    sa.Column('x1', sa.INTEGER(), nullable=True),
    sa.Column('y1', sa.INTEGER(), nullable=True),
    sa.Column('x2', sa.INTEGER(), nullable=True),
    sa.Column('y2', sa.INTEGER(), nullable=True),
    sa.Column('display_name', sa.TEXT(), nullable=True),
    sa.Column('comment', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('roi_id'),
    sa.UniqueConstraint('x1', 'y1', 'x2', 'y2')
    )
    op.create_table('location_t',
    sa.Column('location_id', sa.INTEGER(), nullable=True),
    sa.Column('site_name', sa.TEXT(), nullable=True),
    sa.Column('location', sa.TEXT(), nullable=True),
    sa.Column('longitude', sa.REAL(), nullable=True),
    sa.Column('latitude', sa.REAL(), nullable=True),
    sa.Column('randomized', sa.INTEGER(), nullable=True),
    sa.Column('utc_offset', sa.REAL(), nullable=True),
    sa.PrimaryKeyConstraint('location_id'),
    sa.UniqueConstraint('site_name', 'location')
    )
    op.create_table('date_t',
    sa.Column('date_id', sa.INTEGER(), nullable=True),
    sa.Column('sql_date', sa.TEXT(), nullable=True),
    sa.Column('date', sa.TEXT(), nullable=True),
    sa.Column('day', sa.INTEGER(), nullable=True),
    sa.Column('day_year', sa.INTEGER(), nullable=True),
    sa.Column('julian_day', sa.REAL(), nullable=True),
    sa.Column('weekday', sa.TEXT(), nullable=True),
    sa.Column('weekday_abbr', sa.TEXT(), nullable=True),
    sa.Column('weekday_num', sa.INTEGER(), nullable=True),
    sa.Column('month_num', sa.INTEGER(), nullable=True),
    sa.Column('month', sa.TEXT(), nullable=True),
    sa.Column('month_abbr', sa.TEXT(), nullable=True),
    sa.Column('year', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('date_id')
    )
    op.create_table('config_t',
    sa.Column('section', sa.TEXT(), nullable=True),
    sa.Column('property', sa.TEXT(), nullable=True),
    sa.Column('value', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('section', 'property')
    )
    op.create_table('observer_t',
    sa.Column('observer_id', sa.INTEGER(), nullable=True),
    sa.Column('family_name', sa.TEXT(), nullable=True),
    sa.Column('surname', sa.TEXT(), nullable=True),
    sa.Column('affiliation', sa.TEXT(), nullable=True),
    sa.Column('acronym', sa.TEXT(), nullable=True),
    sa.Column('valid_since', sa.TEXT(), nullable=True),
    sa.Column('valid_until', sa.TEXT(), nullable=True),
    sa.Column('valid_state', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('observer_id'),
    sa.UniqueConstraint('family_name', 'surname', 'affiliation', 'acronym', 'valid_since', 'valid_until')
    )
    op.create_table('image_t',
    sa.Column('image_id', sa.INTEGER(), nullable=True),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.Column('directory', sa.TEXT(), nullable=False),
    sa.Column('hash', sa.BLOB(), nullable=True),
    sa.Column('iso', sa.TEXT(), nullable=True),
    sa.Column('gain', sa.REAL(), nullable=True),
    sa.Column('exptime', sa.REAL(), nullable=True),
    sa.Column('focal_length', sa.REAL(), nullable=True),
    sa.Column('f_number', sa.REAL(), nullable=True),
    sa.Column('imagetype', sa.TEXT(), nullable=True),
    sa.Column('flagged', sa.INTEGER(), nullable=True),
    sa.Column('session', sa.INTEGER(), nullable=False),
    sa.Column('date_id', sa.INTEGER(), nullable=False),
    sa.Column('time_id', sa.INTEGER(), nullable=False),
    sa.Column('camera_id', sa.INTEGER(), nullable=False),
    sa.Column('location_id', sa.INTEGER(), nullable=False),
    sa.Column('observer_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['camera_id'], ['camera_t.camera_id'], ),
    sa.ForeignKeyConstraint(['date_id'], ['date_t.date_id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['location_t.location_id'], ),
    sa.ForeignKeyConstraint(['observer_id'], ['observer_t.observer_id'], ),
    sa.ForeignKeyConstraint(['time_id'], ['time_t.time_id'], ),
    sa.PrimaryKeyConstraint('image_id'),
    sa.UniqueConstraint('hash')
    )
    op.create_table('time_t',
    sa.Column('time_id', sa.INTEGER(), nullable=True),
    sa.Column('time', sa.TEXT(), nullable=True),
    sa.Column('hour', sa.INTEGER(), nullable=True),
    sa.Column('minute', sa.INTEGER(), nullable=True),
    sa.Column('second', sa.INTEGER(), nullable=True),
    sa.Column('day_fraction', sa.REAL(), nullable=True),
    sa.PrimaryKeyConstraint('time_id')
    )
    op.create_table('camera_t',
    sa.Column('camera_id', sa.INTEGER(), nullable=True),
    sa.Column('model', sa.TEXT(), nullable=True),
    sa.Column('bias', sa.INTEGER(), nullable=True),
    sa.Column('extension', sa.TEXT(), nullable=True),
    sa.Column('header_type', sa.TEXT(), nullable=True),
    sa.Column('bayer_pattern', sa.TEXT(), nullable=True),
    sa.Column('width', sa.INTEGER(), server_default=sa.text('0'), nullable=True),
    sa.Column('length', sa.INTEGER(), server_default=sa.text('0'), nullable=True),
    sa.Column('x_pixsize', sa.REAL(), nullable=True),
    sa.Column('y_pixsize', sa.REAL(), nullable=True),
    sa.PrimaryKeyConstraint('camera_id'),
    sa.UniqueConstraint('model')
    )
    op.create_table('sky_brightness_t',
    sa.Column('image_id', sa.INTEGER(), nullable=False),
    sa.Column('roi_id', sa.INTEGER(), nullable=False),
    sa.Column('aver_signal_R', sa.REAL(), nullable=True),
    sa.Column('vari_signal_R', sa.REAL(), nullable=True),
    sa.Column('aver_signal_G1', sa.REAL(), nullable=True),
    sa.Column('vari_signal_G1', sa.REAL(), nullable=True),
    sa.Column('aver_signal_G2', sa.REAL(), nullable=True),
    sa.Column('vari_signal_G2', sa.REAL(), nullable=True),
    sa.Column('aver_signal_B', sa.REAL(), nullable=True),
    sa.Column('vari_signal_B', sa.REAL(), nullable=True),
    sa.Column('published', sa.INTEGER(), server_default=sa.text('0'), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image_t.image_id'], ),
    sa.ForeignKeyConstraint(['roi_id'], ['roi_t.roi_id'], ),
    sa.PrimaryKeyConstraint('image_id', 'roi_id')
    )
    # ### end Alembic commands ###
