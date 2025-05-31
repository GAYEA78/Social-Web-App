from app.utils.database import get_db


class Resident:
    def __init__(
        self,
        resident_id,
        name,
        email,
        phone_number=None,
        interests=None,
        date_of_birth=None,
        profile_image=None,
        username=None,
        hashed_password=None,
    ):
        self.resident_id = resident_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.interests = interests
        self.date_of_birth = date_of_birth
        self.profile_image = profile_image
        self.username = username
        self.hashed_password = hashed_password

    @staticmethod
    def create(
        name,
        email,
        phone_number=None,
        interests=None,
        date_of_birth=None,
        profile_image=None,
        username=None,
        hashed_password=None,
    ):
        if not name or not email:
            raise ValueError("Name and email are required")
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO resident
               (name, email, phone_number, interests, date_of_birth,
                profile_image, username, hashed_password, is_deleted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                name,
                email,
                phone_number,
                interests,
                date_of_birth,
                profile_image,
                username,
                hashed_password,
            ),
        )
        db.commit()
        return cursor.lastrowid

    def soft_delete(self):
        """Mark the resident as deleted instead of hard deleting."""
        db = get_db()
        db.execute(
            """UPDATE resident
               SET is_deleted = 1
               WHERE resident_id = ?""",
            (self.resident_id,),
        )
        db.commit()

    @staticmethod
    def get(resident_id):
        db = get_db()
        row = db.execute(
            """SELECT * FROM resident
               WHERE resident_id = ? AND is_deleted = 0""",
            (resident_id,),
        ).fetchone()
        if row is None:
            return None
        return Resident(**row)

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute(
            """SELECT * FROM resident
               WHERE is_deleted = 0"""
        ).fetchall()
        return [Resident(**row) for row in rows]

    def update(self):
        db = get_db()
        db.execute(
            """UPDATE resident SET
               name = ?, email = ?, phone_number = ?, interests = ?,
               date_of_birth = ?, profile_image = ?, username = ?, hashed_password = ?
               WHERE resident_id = ?""",
            (
                self.name,
                self.email,
                self.phone_number,
                self.interests,
                self.date_of_birth,
                self.profile_image,
                self.username,
                self.hashed_password,
                self.resident_id,
            ),
        )
        db.commit()

    def delete(self):
        db = get_db()
        db.execute("DELETE FROM resident WHERE resident_id = ?", (self.resident_id,))
        db.commit()
