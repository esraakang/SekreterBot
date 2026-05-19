from sqlalchemy import inspect, text

from app import db


def upgrade_db_schema():
    """Mevcut SQLite tablolarina eksik sutunlari ekler (create_all degistirmez)."""
    inspector = inspect(db.engine)
    if "message" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("message")}
    if "created_at" not in columns:
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE message ADD COLUMN created_at DATETIME"))
            conn.execute(
                text("UPDATE message SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            )

    # Eski semada index yoksa olustur
    indexes = {idx["name"] for idx in inspector.get_indexes("message")}
    if "ix_message_user_id" not in indexes:
        with db.engine.begin() as conn:
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_message_user_id ON message (user_id)")
            )
