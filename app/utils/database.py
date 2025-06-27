import os
import psycopg2
import click
from flask import current_app, g
from flask.cli import with_appcontext
from psycopg2.extras import RealDictCursor

from app.utils.logger import setup_logger

log = setup_logger(__name__)


def get_db():
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set!")
        g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def check_db_health():
    """Check if the database is accessible and has the correct schema."""
    try:
        db = get_db()
        cur = db.cursor()

        # Check if essential tables exist
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        tables = [row["table_name"] for row in cur.fetchall()]
        required_tables = {"resident", "activity_group", "event", "review"}
        existing_tables = set(tables)

        missing_tables = required_tables - existing_tables
        if missing_tables:
            log.error(f"Missing required tables: {missing_tables}")
            return False

        # Check if test user exists
        cur.execute("SELECT resident_id FROM resident WHERE username = 'testuser'")
        test_user = cur.fetchone()
        if not test_user:
            log.warning("Test user not found in database")
            return False

        return True
    except Exception as e:
        log.error(f"Database health check failed: {str(e)}")
        return False


def init_db(app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with current_app.open_resource('utils/schema.sql') as f:
            schema_sql = f.read().decode('utf8')
            cur.execute(schema_sql)
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db(current_app)
    click.echo('Initialized the database.')
