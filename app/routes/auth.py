import sqlite3
import psycopg2
import psycopg2.extras
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_required, login_user, logout_user

from app.models.users import User

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"], cursor_factory=psycopg2.extras.RealDictCursor)
    return g.db


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                user_id = User.create(username, password)
                if user_id is None:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("auth.login"))
            except Exception as e:
                error = f"An error occurred: {str(e)}"
        else:
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.validate(username, password)

        if user is None:
            error = 'Incorrect username or password.'

        if error is None:
            login_user(user)
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html')


@auth_bp.route("/profile")
@login_required
def profile():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM resident WHERE resident_id = $1", [current_user.resident_id]
    )
    customer = cur.fetchone()

    return render_template("auth/profile.html", customer=customer)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
