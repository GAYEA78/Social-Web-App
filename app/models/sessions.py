from app.utils.database import get_db


class Session:
    def __init__(self, id, activity_group_name, event_id, date, attendance, agenda):
        self.id = id
        self.activity_group_name = activity_group_name
        self.event_id = event_id
        self.date = date
        self.attendance = attendance
        self.agenda = agenda

    @staticmethod
    def create(activity_group_name, event_id, date, attendance, agenda):
        if attendance < 0:
            raise ValueError("Attendance must be non-negative")
        if not activity_group_name or not event_id or not date:
            raise ValueError("Activity group name, event ID, and date are required")
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO session (activity_group_name, event_id, date, attendance, agenda, is_deleted)
               VALUES (?, ?, ?, ?, ?, 0)""",
            (activity_group_name, event_id, date, attendance, agenda),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get(session_id):
        db = get_db()
        session = db.execute(
            """SELECT * FROM session WHERE id = ? AND is_deleted = 0""", (session_id,)
        ).fetchone()

        if session is None:
            return None

        return Session(
            id=session["id"],
            activity_group_name=session["activity_group_name"],
            event_id=session["event_id"],
            date=session["date"],
            attendance=session["attendance"],
            agenda=session["agenda"],
        )

    @staticmethod
    def get_all(page=1, per_page=10):
        """Fetch all sessions with pagination."""
        db = get_db()
        offset = (page - 1) * per_page
        sessions = db.execute(
            """SELECT * FROM session
               WHERE is_deleted = 0
               ORDER BY date DESC
               LIMIT ? OFFSET ?""",
            (per_page, offset),
        ).fetchall()
        return sessions

    @staticmethod
    def get_by_event(event_id, page=1, per_page=10):
        """Fetch sessions by event ID with pagination."""
        db = get_db()
        offset = (page - 1) * per_page
        sessions = db.execute(
            """SELECT * FROM session
               WHERE event_id = ? AND is_deleted = 0
               ORDER BY date DESC
               LIMIT ? OFFSET ?""",
            (event_id, per_page, offset),
        ).fetchall()
        return sessions

    def update(self):
        if self.attendance < 0:
            raise ValueError("Attendance must be non-negative")
        db = get_db()
        db.execute(
            """UPDATE session
               SET activity_group_name = ?, event_id = ?, date = ?, attendance = ?, agenda = ?
               WHERE id = ? AND is_deleted = 0""",
            (
                self.activity_group_name,
                self.event_id,
                self.date,
                self.attendance,
                self.agenda,
                self.id,
            ),
        )
        db.commit()

    def delete(self):
        """Hard delete the session from the database."""
        db = get_db()
        db.execute("DELETE FROM session WHERE id = ?", (self.id,))
        db.commit()

    def soft_delete(self):
        """Mark the session as deleted instead of hard deleting."""
        db = get_db()
        db.execute(
            """UPDATE session
               SET is_deleted = 1
               WHERE id = ?""",
            (self.id,),
        )
        db.commit()
