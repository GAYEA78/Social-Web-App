import os
import secrets

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from app.models.users import User
from app.routes import init_app
from app.utils.database import check_db_health, close_db, init_db, get_db
from app.utils.init_db import init_db
from app.utils.logger import setup_logger

load_dotenv()

log = setup_logger(__name__)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    secret_key = secrets.token_hex(32)
    app.secret_key = secret_key
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'activity.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    init_db(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Create admin user if it doesn't exist
    with app.app_context():
        db = get_db()
        admin = db.execute(
            "SELECT * FROM resident WHERE role = 'admin'"
        ).fetchone()
        
        if not admin:
            from werkzeug.security import generate_password_hash
            db.execute(
                """
                INSERT INTO resident (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                ('admin', 'admin@example.com', generate_password_hash('admin'), 'admin')
            )
            db.commit()

    app.teardown_appcontext(close_db)
    
    # Register all blueprints
    init_app(app=app)

    return app
