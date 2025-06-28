from app.utils.database import get_db

class Prerequisite:
    def __init__(
        self,
        event_id,
        prerequisite_event_id,
        minimum_performance,
        qualification_period,
        is_waiver_allowed,
    ):
        self.event_id = event_id
        self.prerequisite_event_id = prerequisite_event_id
        self.minimum_performance = minimum_performance
        self.qualification_period = qualification_period
        self.is_waiver_allowed = is_waiver_allowed

    @staticmethod
    def create(event_id, prerequisite_event_id, minimum_performance, qualification_period, is_waiver_allowed):
        db = get_db()
        cursor = db.cursor()

        if event_id == prerequisite_event_id:
            raise ValueError("An event cannot be its own prerequisite")
        
        # Check if prerequisite already exists
        cursor.execute(
            "SELECT * FROM prerequisite WHERE event_id = %s AND prerequisite_event_id = %s",
            (event_id, prerequisite_event_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            raise ValueError("This prerequisite already exists")
        
        # Insert new prerequisite
        cursor.execute(
            """
            INSERT INTO prerequisite (
                event_id, prerequisite_event_id, minimum_performance,
                qualification_period, is_waiver_allowed
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (event_id, prerequisite_event_id, minimum_performance, qualification_period, is_waiver_allowed)
        )
        db.commit()
        cursor.close()

    @staticmethod
    def remove(prerequisite_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM prerequisite WHERE id = %s",
            (prerequisite_id,)
        )
        db.commit()
        cursor.close()

    @staticmethod
    def get_prerequisites(event_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.prerequisite_event_id = e.id
            WHERE p.event_id = %s
            """,
            (event_id,)
        )
        prerequisites = cursor.fetchall()
        cursor.close()
        return [dict(prereq) for prereq in prerequisites]

    @staticmethod
    def check_prerequisites(user_id, event_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.prerequisite_event_id = e.id
            WHERE p.event_id = %s
            """,
            (event_id,)
        )
        prerequisites = cursor.fetchall()

        if not prerequisites:
            cursor.close()
            return True, []

        unmet_prerequisites = []
        for prereq in prerequisites:
            cursor.execute(
                """
                SELECT r.*, s.attendance
                FROM registrations r
                JOIN session s ON r.event_id = s.event_id
                WHERE r.user_id = %s AND r.event_id = %s
                AND r.status = 'completed'
                AND s.attendance >= %s
                AND s.date >= CURRENT_DATE - INTERVAL '%s days'
                """,
                (
                    user_id,
                    prereq['prerequisite_event_id'],
                    prereq['minimum_performance'],
                    prereq['qualification_period'],
                )
            )
            registration = cursor.fetchone()
            if not registration:
                unmet_prerequisites.append({
                    'event_name': prereq['activity_group_name'],
                    'date': prereq['date'],
                    'minimum_performance': prereq['minimum_performance'],
                    'qualification_period': prereq['qualification_period'],
                    'is_waiver_allowed': prereq['is_waiver_allowed'],
                })
        cursor.close()
        return len(unmet_prerequisites) == 0, unmet_prerequisites

    @staticmethod
    def get_dependent_events(prerequisite_event_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.event_id = e.id
            WHERE p.prerequisite_event_id = %s
            """,
            (prerequisite_event_id,)
        )
        dependent_events = cursor.fetchall()
        cursor.close()
        return [dict(dep) for dep in dependent_events]
