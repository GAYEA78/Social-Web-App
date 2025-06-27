from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from app.utils.database import get_db
from psycopg2 import IntegrityError 

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, resident_id, username, hashed_password, role='user'):
        self.id = resident_id
        self.username = username
        self.hashed_password = hashed_password
        self.role = role

    @property
    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def validate(username, password):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT resident_id, username, password_hash, role FROM resident WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()

        if user is None:
            return None

        if bcrypt.check_password_hash(user["password_hash"], password):
            return User(
                user["resident_id"],
                user["username"],
                user["password_hash"],
                user["role"]
            )
        return None

    @staticmethod
    def get(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT resident_id, username, password_hash, role FROM resident WHERE resident_id = %s",
            (user_id,),
        )
        user = cursor.fetchone()

        if user is None:
            return None

        return User(
            user["resident_id"],
            user["username"],
            user["password_hash"],
            user["role"]
        )

    @staticmethod
    def create(username, password, role='user'):
        db = get_db()
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        try:
            cursor = db.cursor()
            cursor.execute(
                """INSERT INTO resident (username, password_hash, role)
                   VALUES (%s, %s, %s)""",
                (username, hashed_password, role)
            )
            db.commit()
            return cursor.lastrowid
        except IntegrityError:
            db.rollback()
            return None

    def update_password(self, new_password):
        if not new_password:
            raise ValueError("Password cannot be empty")
        db = get_db()
        cursor = db.cursor()
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        cursor.execute(
            """UPDATE resident
               SET password_hash = %s
               WHERE resident_id = %s""",
            (hashed_password, self.id),
        )
        db.commit()

    def soft_delete(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE resident
               SET is_deleted = 1
               WHERE resident_id = %s""",
            (self.id,),
        )
        db.commit()
