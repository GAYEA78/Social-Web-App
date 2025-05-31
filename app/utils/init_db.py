import sqlite3

from app.utils.logger import setup_logger

log = setup_logger(__name__)

DB_VERSION = 1  # Increment this when making schema changes


def get_db_version(db):
    try:
        return db.execute("SELECT version FROM db_version").fetchone()[0]
    except sqlite3.OperationalError:
        return 0


def init_db(app):
    """Initialize the database with required tables."""
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        db.execute("PRAGMA foreign_keys = ON")

        current_version = get_db_version(db)
        if current_version < DB_VERSION:
            log.info(f"Upgrading database from version {current_version} to {DB_VERSION}")
            with open("app/utils/schema.sql", "r") as f:
                db.executescript(f.read())

            # Create or update version table
            db.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER)")
            db.execute("DELETE FROM db_version")
            db.execute("INSERT INTO db_version VALUES (?)", (DB_VERSION,))

            db.commit()
            log.info("Database schema updated successfully")
        else:
            log.info("Database schema is up to date")
