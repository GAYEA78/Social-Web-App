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
    def create(
        event_id,
        prerequisite_event_id,
        minimum_performance,
        qualification_period,
        is_waiver_allowed,
    ):
        """Create a new prerequisite."""
        db = get_db()
        if event_id == prerequisite_event_id:
            raise ValueError("An event cannot be its own prerequisite")
        
        # Check if prerequisite already exists
        existing = db.execute(
            "SELECT * FROM prerequisite WHERE event_id = ? AND prerequisite_event_id = ?",
            (event_id, prerequisite_event_id)
        ).fetchone()
        
        if existing:
            raise ValueError("This prerequisite already exists")
        
        # Insert new prerequisite
        db.execute(
            """
            INSERT INTO prerequisite (
                event_id, prerequisite_event_id, minimum_performance,
                qualification_period, is_waiver_allowed
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, prerequisite_event_id, minimum_performance,
             qualification_period, is_waiver_allowed)
        )
        db.commit()

    @staticmethod
    def remove(prerequisite_id):
        """Remove a prerequisite by its ID."""
        db = get_db()
        db.execute(
            "DELETE FROM prerequisite WHERE id = ?",
            (prerequisite_id,)
        )
        db.commit()

    @staticmethod
    def get_prerequisites(event_id):
        """Get all prerequisites for an event."""
        db = get_db()
        prerequisites = db.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.prerequisite_event_id = e.id
            WHERE p.event_id = ?
            """,
            (event_id,)
        ).fetchall()
        
        return [dict(prereq) for prereq in prerequisites]

    @staticmethod
    def check_prerequisites(user_id, event_id):
        """Check if a user meets all prerequisites for an event."""
        db = get_db()
        prerequisites = db.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.prerequisite_event_id = e.id
            WHERE p.event_id = ?
            """,
            (event_id,)
        ).fetchall()
        
        if not prerequisites:
            return True, []  # No prerequisites required
        
        unmet_prerequisites = []
        for prereq in prerequisites:
            # Check if user has completed the prerequisite event
            registration = db.execute(
                """
                SELECT r.*, s.attendance
                FROM registrations r
                JOIN session s ON r.event_id = s.event_id
                WHERE r.user_id = ? AND r.event_id = ?
                AND r.status = 'completed'
                AND s.attendance >= ?
                AND s.date >= date('now', ? || ' days')
                """,
                (user_id, prereq['prerequisite_event_id'],
                 prereq['minimum_performance'],
                 f"-{prereq['qualification_period']}")
            ).fetchone()
            
            if not registration:
                unmet_prerequisites.append({
                    'event_name': prereq['activity_group_name'],
                    'date': prereq['date'],
                    'minimum_performance': prereq['minimum_performance'],
                    'qualification_period': prereq['qualification_period'],
                    'is_waiver_allowed': prereq['is_waiver_allowed']
                })
        
        return len(unmet_prerequisites) == 0, unmet_prerequisites

    @staticmethod
    def get_dependent_events(prerequisite_event_id):
        db = get_db()
        dependent_events = db.execute(
            """SELECT p.*, e.activity_group_name, e.date
               FROM prerequisite p
               JOIN event e ON p.event_id = e.event_id
               WHERE p.prerequisite_event_id = ?""",
            (prerequisite_event_id,),
        ).fetchall()
        return dependent_events
