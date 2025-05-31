from app.utils.database import get_db


class Member:
    def __init__(self, resident_id, activity_group_name, join_date, role):
        self.resident_id = resident_id
        self.activity_group_name = activity_group_name
        self.join_date = join_date
        self.role = role

    @staticmethod
    def add_member(resident_id, activity_group_name, join_date, role):
        db = get_db()
        db.execute(
            """INSERT INTO member (resident_id, activity_group_name, join_date, role)
               VALUES (?, ?, ?, ?)""",
            (resident_id, activity_group_name, join_date, role),
        )
        db.commit()

    @staticmethod
    def remove_member(resident_id, activity_group_name):
        db = get_db()
        db.execute(
            """DELETE FROM member
               WHERE resident_id = ? AND activity_group_name = ?""",
            (resident_id, activity_group_name),
        )
        db.commit()

    @staticmethod
    def get_members(activity_group_name):
        db = get_db()
        members = db.execute(
            """SELECT m.*, r.name, r.email
               FROM member m
               JOIN resident r ON m.resident_id = r.resident_id
               WHERE m.activity_group_name = ?""",
            (activity_group_name,),
        ).fetchall()
        return members

    @staticmethod
    def get_memberships(resident_id):
        db = get_db()
        memberships = db.execute(
            """SELECT m.*, ag.category, ag.description
               FROM member m
               JOIN activity_group ag ON m.activity_group_name = ag.name
               WHERE m.resident_id = ?""",
            (resident_id,),
        ).fetchall()
        return memberships

    @staticmethod
    def validate_membership(resident_id, activity_group_name):
        db = get_db()
        membership = db.execute(
            """SELECT * FROM member
               WHERE resident_id = ? AND activity_group_name = ?""",
            (resident_id, activity_group_name),
        ).fetchone()
        return membership is not None
