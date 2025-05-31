from app.utils.database import get_db
from datetime import datetime


class Event:
    def __init__(self, id, activity_group_name, date, max_participants=None,
                 cost=0, registration_required=False, registration_deadline=None,
                 created_by=None):
        self.id = id
        self.activity_group_name = activity_group_name
        self.date = date
        self.max_participants = max_participants
        self.cost = cost
        self.registration_required = registration_required
        self.registration_deadline = registration_deadline
        self.created_by = created_by

    @property
    def event_id(self):
        return self.id

    @staticmethod
    def create(activity_group_name, date, max_participants=None, cost=0,
               registration_required=False, registration_deadline=None,
               location_id=None, created_by=None):
        """Create a new event."""
        db = get_db()
        db.execute(
            """
            INSERT INTO event (
                activity_group_name, date, max_participants, cost,
                registration_required, registration_deadline,
                location_id, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (activity_group_name, date, max_participants, cost,
             registration_required, registration_deadline,
             location_id, created_by)
        )
        db.commit()

    @staticmethod
    def get(event_id):
        """Get an event by ID."""
        db = get_db()
        event = db.execute(
            """
            SELECT e.*, l.address, l.city, l.state, l.zip_code
            FROM event e
            LEFT JOIN location l ON e.location_id = l.id
            WHERE e.id = ?
            """,
            (event_id,)
        ).fetchone()
        
        return dict(event) if event else None

    @staticmethod
    def get_all(search_query=None, exclude_event_id=None):
        """Get all events, optionally filtered by search query."""
        db = get_db()
        query = """
            SELECT e.*, l.address, l.city, l.state, l.zip_code
            FROM event e
            LEFT JOIN location l ON e.location_id = l.id
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += """
                AND (
                    e.activity_group_name LIKE ?
                    OR l.address LIKE ?
                    OR l.city LIKE ?
                )
            """
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])
        
        if exclude_event_id:
            query += " AND e.id != ?"
            params.append(exclude_event_id)
        
        query += " ORDER BY e.date DESC"
        
        events = db.execute(query, params).fetchall()
        return [dict(event) for event in events]

    @staticmethod
    def update(event_id, **kwargs):
        """Update an event's details."""
        db = get_db()
        allowed_fields = {
            'activity_group_name', 'date', 'max_participants', 'cost',
            'registration_required', 'registration_deadline', 'location_id'
        }
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        query = f"UPDATE event SET {set_clause} WHERE id = ?"
        
        db.execute(query, list(updates.values()) + [event_id])
        db.commit()

    @staticmethod
    def delete(event_id):
        """Delete an event and its related records."""
        db = get_db()
        # Delete prerequisites
        db.execute("DELETE FROM prerequisite WHERE event_id = ?", (event_id,))
        db.execute("DELETE FROM prerequisite WHERE prerequisite_event_id = ?", (event_id,))
        
        # Delete registrations and waitlist
        db.execute("DELETE FROM registrations WHERE event_id = ?", (event_id,))
        db.execute("DELETE FROM waitlist WHERE event_id = ?", (event_id,))
        
        # Delete sessions
        db.execute("DELETE FROM session WHERE event_id = ?", (event_id,))
        
        # Delete the event
        db.execute("DELETE FROM event WHERE id = ?", (event_id,))
        db.commit()

    @staticmethod
    def get_registered_users(event_id):
        """Get all users registered for an event."""
        db = get_db()
        users = db.execute(
            """
            SELECT r.*, u.username, u.email
            FROM registrations r
            JOIN resident u ON r.user_id = u.id
            WHERE r.event_id = ? AND r.status = 'registered'
            """,
            (event_id,)
        ).fetchall()
        
        return [dict(user) for user in users]

    @staticmethod
    def get_waitlisted_users(event_id):
        """Get all users on the waitlist for an event."""
        db = get_db()
        users = db.execute(
            """
            SELECT w.*, u.username, u.email
            FROM waitlist w
            JOIN resident u ON w.user_id = u.id
            WHERE w.event_id = ?
            ORDER BY w.created_at ASC
            """,
            (event_id,)
        ).fetchall()
        
        return [dict(user) for user in users]

    @staticmethod
    def register_user(event_id, user_id):
        """Register a user for an event."""
        db = get_db()
        event = Event.get(event_id)
        if not event:
            raise ValueError("Event not found")
        
        # Check if user is already registered
        existing = db.execute(
            "SELECT * FROM registrations WHERE event_id = ? AND user_id = ?",
            (event_id, user_id)
        ).fetchone()
        
        if existing:
            raise ValueError("User is already registered for this event")
        
        # Check if event is full
        if event['max_participants']:
            registered_count = db.execute(
                """
                SELECT COUNT(*) as count
                FROM registrations
                WHERE event_id = ? AND status = 'registered'
                """,
                (event_id,)
            ).fetchone()['count']
            
            if registered_count >= event['max_participants']:
                # Add to waitlist
                db.execute(
                    """
                    INSERT INTO waitlist (event_id, user_id)
                    VALUES (?, ?)
                    """,
                    (event_id, user_id)
                )
                db.commit()
                return False  # Added to waitlist
        
        # Register user
        db.execute(
            """
            INSERT INTO registrations (event_id, user_id, status)
            VALUES (?, ?, 'registered')
            """,
            (event_id, user_id)
        )
        db.commit()
        return True  # Successfully registered

    @staticmethod
    def cancel_registration(event_id, user_id):
        """Cancel a user's registration for an event."""
        db = get_db()
        # Remove registration
        db.execute(
            """
            DELETE FROM registrations
            WHERE event_id = ? AND user_id = ?
            """,
            (event_id, user_id)
        )
        
        # Check if there are waitlisted users
        waitlisted = db.execute(
            """
            SELECT * FROM waitlist
            WHERE event_id = ?
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (event_id,)
        ).fetchone()
        
        if waitlisted:
            # Register the first waitlisted user
            db.execute(
                """
                INSERT INTO registrations (event_id, user_id, status)
                VALUES (?, ?, 'registered')
                """,
                (event_id, waitlisted['user_id'])
            )
            
            # Remove from waitlist
            db.execute(
                """
                DELETE FROM waitlist
                WHERE event_id = ? AND user_id = ?
                """,
                (event_id, waitlisted['user_id'])
            )
        
        db.commit()

    @staticmethod
    def get_prerequisites(event_id):
        db = get_db()
        prerequisites = db.execute(
            """SELECT p.*, e.activity_group_name, e.date
               FROM prerequisite p
               JOIN event e ON p.prerequisite_event_id = e.event_id
               WHERE p.event_id = ?""",
            (event_id,),
        ).fetchall()
        return prerequisites

    def update(self):
        if self.max_participants < 0 or self.cost < 0:
            raise ValueError("Max participants and cost must be non-negative")
        db = get_db()
        db.execute(
            """UPDATE event
               SET activity_group_name = ?, date = ?, location_id = ?,
                   max_participants = ?, cost = ?, registration_required = ?,
                   registration_deadline = ?
               WHERE event_id = ?""",
            (
                self.activity_group_name,
                self.date,
                self.location_id,
                self.max_participants,
                self.cost,
                self.registration_required,
                self.registration_deadline,
                self.id,
            ),
        )
        db.commit()

    def delete(self):
        db = get_db()
        # First delete all prerequisites
        db.execute("DELETE FROM prerequisite WHERE event_id = ?", (self.id,))
        db.execute("DELETE FROM prerequisite WHERE prerequisite_event_id = ?", (self.id,))
        # Then delete the event
        db.execute("DELETE FROM event WHERE event_id = ?", (self.id,))
        db.commit()

    @staticmethod
    def event_registration(event_id, user_id):
        db = get_db()
        event = db.execute(
            """SELECT max_participants, 
                      (SELECT count(*) FROM registrations WHERE event_id = ?) AS current_participants
               FROM events WHERE id = ?""",
            (event_id, event_id),
        ).fetchone()

        if not event:
            return {"success": False, "message": "Event not found"}

        if event["current_participants"] < event["max_participants"]:
            db.execute(
                """INSERT INTO registrations (event_id, user_id)
                   VALUES (?, ?)""",
                (event_id, user_id),
            )
            db.commit()
            return {"success": True, "message": "Successfully registered for the event"}

        # Check if the user is already on the waitlist
        if Event.get_waitlist(user_id, event_id):
            return {"success": False, "message": "User is already on the waitlist"}

        # Add the user to the waitlist
        db.execute(
            """INSERT INTO waitlist (event_id, user_id)
               VALUES (?, ?)""",
            (event_id, user_id),
        )
        db.commit()
        return {"success": True, "message": "Event is full. Added to the waitlist"}

    def soft_delete(self):
        """Mark the event as deleted instead of hard deleting."""
        db = get_db()
        db.execute(
            """UPDATE events
               SET is_deleted = 1
               WHERE id = ?""",
            (self.id,),
        )
        db.commit()

    @staticmethod
    def notify_waitlist(event_id):
        db = get_db()
        waitlist_user = db.execute(
            """SELECT w.id, w.user_id, r.email
               FROM waitlist w
               JOIN resident r ON w.user_id = r.resident_id
               WHERE w.event_id = ? AND w.status = 'waiting'
               ORDER BY w.added_at ASC
               LIMIT 1""",
            (event_id,),
        ).fetchone()

        if not waitlist_user:
            return {"success": False, "message": "No users on the waitlist"}

        # Simulate sending a notification
        print(f"Notifying user {waitlist_user['email']} about an open spot in event {event_id}")

        # Update waitlist status to 'notified'
        db.execute(
            """UPDATE waitlist
               SET status = 'notified'
               WHERE id = ?""",
            (waitlist_user["id"],),
        )
        db.commit()
        return {"success": True, "message": "User notified", "email": waitlist_user["email"]}

    @staticmethod
    def confirm_waitlist(event_id, user_id):
        db = get_db()
        waitlist_entry = db.execute(
            """SELECT * FROM waitlist
               WHERE event_id = ? AND user_id = ? AND status = 'notified'""",
            (event_id, user_id),
        ).fetchone()

        if not waitlist_entry:
            return {"success": False, "message": "No notification found for this user"}

        # Register the user
        db.execute(
            """INSERT INTO registrations (event_id, user_id)
               VALUES (?, ?)""",
            (event_id, user_id),
        )
        db.commit()

        # Remove the user from the waitlist
        db.execute(
            """DELETE FROM waitlist
               WHERE id = ?""",
            (waitlist_entry["id"],),
        )
        db.commit()
        return {"success": True, "message": "Waitlist spot confirmed and registered"}

    @staticmethod
    def event_notification():
        db = get_db()
        events = db.execute(
            """SELECT e.id, e.activity_group_name, e.date, u.email
            FROM event e
            JOIN registrations r ON r.event_id = e.id 
            JOIN users u ON r.user_id = u.id
            WHERE e.date BETWEEN datetime('now') AND datetime('now', '+1 day')"""
        ).fetchall()

        for event in events:
            print(
                f"Sending notification to {event['email']} for event {event['activity_group_name']}"
            )

    @staticmethod
    def search_events(search_term, date, location):
        db = get_db()
        query = """SELECT e.id, e.activity_group_name, e.date, e.location_id
                FROM event e
                LEFT JOIN locations l on e.location_id = l.id
                WHERE 1=1"""
        params = []
        if search_term:
            query += " AND e.activity_group_name LIKE ?"
            params.append(f"%{search_term}%")
        if date:
            query += " AND e.date = ?"
            params.append(date)
        if location:
            query += (
                " AND (l.address LIKE ? OR l.city LIKE ? OR l.state LIKE ? OR l.zip_code LIKE ?)"
            )
            params.extend([f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%"])
        query += " ORDER BY e.date DESC"
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_waitlist(user_id, event_id):
        db = get_db()
        waitlist = db.execute(
            """SELECT w.id, w.event_id, w.user_id
            FROM waitlist w
            JOIN events e ON e.id = w.event_id
            JOIN users u ON u.id = w.user_id
            WHERE w.event_id = ? AND w.user_id = ?""",
            (event_id, user_id),
        ).fetchall()
        return waitlist
