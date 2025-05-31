import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import pytest
from flask import g

from app import create_app
from app.services.activity_groups import ActivityGroupsService


@pytest.fixture
def app():
    # Create a temporary file to store the test database
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)  # Close the file descriptor as we'll use the path with shutil

    # Create the app first to get the main database path
    app = create_app()
    main_db = os.path.join(app.root_path, "activity.db")

    # Copy the main database to our test location
    shutil.copy2(main_db, db_path)

    # Update the app config to use the test database
    app.config.update({"TESTING": True, "DATABASE": db_path})

    yield app

    # Clean up the temporary file
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture
def mock_cursor():
    cursor = Mock()
    return cursor


@pytest.fixture
def mock_db(app, mock_cursor):
    with app.app_context():
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Patch the database connection
        with patch("app.utils.database.get_db", return_value=mock_conn):
            g.db = mock_conn
            yield mock_cursor


@pytest.fixture
def mock_activity_groups_service(mock_db):
    service = ActivityGroupsService()
    # Ensure the cursor is set after initialization
    service.cursor = mock_db
    return service


@pytest.fixture
def mock_user():
    """Create a mock user for testing authentication."""
    return Mock(id=1, username="testuser", resident_id=1, hashed_password="hashed_password")


@pytest.fixture
def login_user(client, mock_user):
    """Simulate a logged-in user for tests that require authentication."""
    with patch("app.models.user.User.validate", return_value=mock_user):
        with patch("flask_login.utils._get_user", return_value=mock_user):
            client.post("/login", data={"username": "testuser", "password": "password"})
            yield mock_user


@pytest.fixture
def mock_bcrypt():
    """Mock the bcrypt password hashing functionality."""
    with patch("app.models.user.bcrypt") as mock:
        mock.check_password_hash.return_value = True
        mock.generate_password_hash.return_value = "hashed_password"
        yield mock
