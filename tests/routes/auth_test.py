from unittest.mock import MagicMock, patch


def test_register_get(client):
    """Test register page loads correctly."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_register_post_success(client, app):
    """Test successful registration."""
    with app.app_context():
        # Mock the database to avoid actual database operations
        with patch("app.routes.auth.get_db") as mock_get_db:
            mock_cursor = MagicMock()
            mock_get_db.return_value = mock_cursor

            # Mock customer check to return a valid resident
            mock_cursor.execute.return_value.fetchone.return_value = {"resident_id": "TESTID"}

            # Mock the bcrypt password hashing
            with patch("app.routes.auth.bcrypt.generate_password_hash") as mock_hash:
                mock_hash.return_value = b"hashed_password"

                response = client.post(
                    "/register",
                    data={"username": "testuser", "password": "testpass", "resident_id": "TESTID"},
                    follow_redirects=True,
                )

                # Check that the user was redirected to login
                assert response.status_code == 200
                assert b"Login" in response.data

                # Check that the database was called correctly
                mock_cursor.execute.assert_any_call(
                    "SELECT id FROM residents WHERE id = ?", ["TESTID"]
                )

                # Check that the user was created
                mock_cursor.execute.assert_any_call(
                    "INSERT INTO users (resident_id, username, hashed_password) VALUES (?, ?, ?)",
                    ("TESTID", "testuser", "hashed_password"),
                )


def test_register_post_existing_user(client, app):
    """Test registration with existing username."""
    with app.app_context():
        # Mock the database to avoid actual database operations
        with patch("app.routes.auth.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock customer check to return a valid customer
            mock_conn.execute.return_value.fetchone.return_value = {"resident_id": "TESTID"}

            # Mock the database to raise IntegrityError (user already exists)
            from sqlite3 import IntegrityError

            mock_conn.execute.side_effect = [
                MagicMock(),  # First call returns successfully (customer check)
                IntegrityError(
                    "UNIQUE constraint failed"
                ),  # Second call raises exception (user insert)
            ]

            # Mock the flash function to capture error messages
            with patch("app.routes.auth.flash") as mock_flash:
                # Test registration with existing username
                response = client.post(
                    "/register",
                    data={
                        "username": "existing_user",
                        "password": "password123",
                        "confirm_password": "password123",
                        "resident_id": "TESTID",
                    },
                    follow_redirects=True,
                )

                # Check that registration failed with appropriate message
                assert response.status_code == 200
                # Verify that flash was called with an error message about existing username
                mock_flash.assert_called_with(
                    "Username already exists or Resident ID already registered", "error"
                )


def test_login_get(client):
    """Test login page loads correctly."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_post_success(client, app):
    """Test successful login."""
    with app.app_context():
        # Mock the User.validate method to return a valid user
        with patch("app.models.users.User.validate") as mock_validate:
            mock_user = MagicMock()
            mock_validate.return_value = mock_user

            # Mock login_user to do nothing
            with patch("app.routes.auth.login_user") as mock_login:
                response = client.post(
                    "/login",
                    data={"username": "testuser", "password": "testpass"},
                    follow_redirects=True,
                )

                # Check that the user was logged in and redirected
                assert response.status_code == 200
                mock_login.assert_called_once_with(mock_user)


def test_login_post_invalid_credentials(client, app):
    """Test login with invalid credentials."""
    with app.app_context():
        # Mock the User.validate method to return None (invalid credentials)
        with patch("app.models.users.User.validate") as mock_validate:
            mock_validate.return_value = None

            response = client.post("/login", data={"username": "testuser", "password": "wrongpass"})

            # Check that the user was shown an error
            assert response.status_code == 200
            assert b"Invalid username or password" in response.data


def test_logout(client, app):
    """Test logout functionality."""
    with app.app_context():
        # Set up a logged-in session
        with client.session_transaction() as sess:
            sess["user_id"] = "TESTID"

        # Test logout
        response = client.get("/logout", follow_redirects=True)

        # Check that the user was logged out and redirected
        assert response.status_code == 200

        # Check that the response contains login-related content
        # (indicating we've been redirected to the home page)
        assert b"Login" in response.data or b"login" in response.data.lower()
