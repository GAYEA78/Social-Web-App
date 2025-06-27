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
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO event (
                activity_group_name, date, max_participants, cost,
                registration_required, registration_deadline,
                location_id, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                activity_group_name, date, max_participants, cost,
                registration_required, registration_deadline,
                location_id, created_by
            )
        )
        db.commit()
        cursor.close()
                   
    @staticmethod
    def get(event_id):
        """Get an event by ID."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT e.*, l.address, l.city, l.state, l.zip_code
            FROM event e
            LEFT JOIN location l ON e.location_id = l.id
            WHERE e.id = %s
            """,
            (event_id,)
        )
        event = cursor.fetchone()
        cursor.close()
        
        return dict(event) if event else None


    @staticmethod
    def get_all(search_query=None, exclude_event_id=None):
        """Get all events, optionally filtered by search query."""
        db = get_db()
        cursor = db.cursor()
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
                    e.activity_group_name ILIKE %s
                    OR l.address ILIKE %s
                    OR l.city ILIKE %s
                )
            """
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])
        
        if exclude_event_id:
            query += " AND e.id != %s"
            params.append(exclude_event_id)
        
        query += " ORDER BY e.date DESC"
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        cursor.close()
        
        return [dict(event) for event in events]


    @staticmethod
    def update(event_id, **kwargs):
        """Update an event's details."""
        db = get_db()
        cursor = db.cursor()
        allowed_fields = {
            'activity_group_name', 'date', 'max_participants', 'cost',
            'registration_required', 'registration_deadline', 'location_id'
        }
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return
        
        set_clause = ', '.join(f"{k} = %s" for k in updates.keys())
        query = f"UPDATE event SET {set_clause} WHERE id = %s"
        
        params = list(updates.values()) + [event_id]
        cursor.execute(query, params)
        db.commit()
        cursor.close()


    @staticmethod
    def delete(event_id):
        """Delete an event and its related records."""
        db = get_db()
        cursor = db.cursor()

        # Delete prerequisites
        cursor.execute("DELETE FROM prerequisite WHERE event_id = %s", (event_id,))
        cursor.execute("DELETE FROM prerequisite WHERE prerequisite_event_id = %s", (event_id,))
        
        # Delete registrations and waitlist
        cursor.execute("DELETE FROM registrations WHERE event_id = %s", (event_id,))
        cursor.execute("DELETE FROM waitlist WHERE event_id = %s", (event_id,))
        
        # Delete sessions
        cursor.execute("DELETE FROM session WHERE event_id = %s", (event_id,))
        
        # Delete the event itself
        cursor.execute("DELETE FROM event WHERE id = %s", (event_id,))
        
        db.commit()
        cursor.close()


    @staticmethod
    def get_registered_users(event_id):
        """Get all users registered for an event."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.*, u.username, u.email
            FROM registrations r
            JOIN resident u ON r.user_id = u.resident_id
            WHERE r.event_id = %s AND r.status = 'registered'
            """,
            (event_id,)
        )
        users = cursor.fetchall()
        cursor.close()
        return [dict(user) for user in users]


    @staticmethod
    def get_waitlisted_users(event_id):
        """Get all users on the waitlist for an event."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT w.*, u.username, u.email
            FROM waitlist w
            JOIN resident u ON w.user_id = u.resident_id
            WHERE w.event_id = %s
            ORDER BY w.created_at ASC
            """,
            (event_id,)
        )
        users = cursor.fetchall()
        cursor.close()
        return [dict(user) for user in users]


    @staticmethod
    def register_user(event_id, user_id):
        """Register a user for an event."""
        db = get_db()
        cursor = db.cursor()

        event = Event.get(event_id)
        if not event:
            cursor.close()
            raise ValueError("Event not found")

        # Check if user is already registered
        cursor.execute(
            "SELECT * FROM registrations WHERE event_id = %s AND user_id = %s",
            (event_id, user_id)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            raise ValueError("User is already registered for this event")

        # Check if event is full
        if event['max_participants']:
            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM registrations
                WHERE event_id = %s AND status = 'registered'
                """,
                (event_id,)
            )
            registered_count = cursor.fetchone()['count']

            if registered_count >= event['max_participants']:
                # Add to waitlist
                cursor.execute(
                    """
                    INSERT INTO waitlist (event_id, user_id)
                    VALUES (%s, %s)
                    """,
                    (event_id, user_id)
                )
                db.commit()
                cursor.close()
                return False  # Added to waitlist

        # Register user
        cursor.execute(
            """
            INSERT INTO registrations (event_id, user_id, status)
            VALUES (%s, %s, 'registered')
            """,
            (event_id, user_id)
        )
        db.commit()
        cursor.close()
        return True  # Successfully registered


    @staticmethod
    def cancel_registration(event_id, user_id):
        """Cancel a user's registration for an event."""
        db = get_db()
        cursor = db.cursor()

        # Remove registration
        cursor.execute(
            """
            DELETE FROM registrations
            WHERE event_id = %s AND user_id = %s
            """,
            (event_id, user_id)
        )

        # Check if there are waitlisted users
        cursor.execute(
            """
            SELECT * FROM waitlist
            WHERE event_id = %s
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (event_id,)
        )
        waitlisted = cursor.fetchone()

        if waitlisted:
            # Register the first waitlisted user
            cursor.execute(
                """
                INSERT INTO registrations (event_id, user_id, status)
                VALUES (%s, %s, 'registered')
                """,
                (event_id, waitlisted['user_id'])
            )

            # Remove from waitlist
            cursor.execute(
                """
                DELETE FROM waitlist
                WHERE event_id = %s AND user_id = %s
                """,
                (event_id, waitlisted['user_id'])
            )

        db.commit()
        cursor.close()


    @staticmethod
    def get_prerequisites(event_id):
        """Retrieve prerequisites for a given event."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT p.*, e.activity_group_name, e.date
            FROM prerequisite p
            JOIN event e ON p.prerequisite_event_id = e.id
            WHERE p.event_id = %s
            """,
            (event_id,),
        )
        prerequisites = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in prerequisites]


    def update(self):
        """Update this event instance in the database."""
        if self.max_participants < 0 or self.cost < 0:
            raise ValueError("Max participants and cost must be non-negative")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE event
            SET activity_group_name = %s, date = %s, location_id = %s,
                max_participants = %s, cost = %s, registration_required = %s,
                registration_deadline = %s
            WHERE id = %s
            """,
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
        cursor.close()


    def delete(self):
        """Delete this event instance and related records from the database."""
        db = get_db()
        cursor = db.cursor()

        # First delete all prerequisites where this event is either the main event or a prerequisite
        cursor.execute("DELETE FROM prerequisite WHERE event_id = %s", (self.id,))
        cursor.execute("DELETE FROM prerequisite WHERE prerequisite_event_id = %s", (self.id,))

        # Delete the event itself
        cursor.execute("DELETE FROM event WHERE id = %s", (self.id,))

        db.commit()
        cursor.close()


    @staticmethod
    def event_registration(event_id, user_id):
        """Register a user for an event, or add them to the waitlist if full."""
        db = get_db()
        cursor = db.cursor()

        # Fetch event capacity and current number of registrations
        cursor.execute(
            """
            SELECT max_participants,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = %s) AS current_participants
            FROM event WHERE id = %s
            """,
            (event_id, event_id),
        )
        event = cursor.fetchone()

        if not event:
            cursor.close()
            return {"success": False, "message": "Event not found"}

        if event["current_participants"] < event["max_participants"]:
            # Event has space - register the user
            cursor.execute(
                """
                INSERT INTO registrations (event_id, user_id)
                VALUES (%s, %s)
                """,
                (event_id, user_id),
            )
            db.commit()
            cursor.close()
            return {"success": True, "message": "Successfully registered for the event"}

        # Check if the user is already on the waitlist
        waitlist = Event.get_waitlist(user_id, event_id)
        if waitlist:
            cursor.close()
            return {"success": False, "message": "User is already on the waitlist"}

        # Add the user to the waitlist
        cursor.execute(
            """
            INSERT INTO waitlist (event_id, user_id)
            VALUES (%s, %s)
            """,
            (event_id, user_id),
        )
        db.commit()
        cursor.close()
        return {"success": True, "message": "Event is full. Added to the waitlist"}


    def soft_delete(self):
        """Mark the event as deleted instead of hard deleting."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE event
            SET is_deleted = TRUE
            WHERE id = %s
            """,
            (self.id,),
        )
        db.commit()
        cursor.close()


    @staticmethod
    def notify_waitlist(event_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT w.id, w.user_id, r.email
            FROM waitlist w
            JOIN resident r ON w.user_id = r.resident_id
            WHERE w.event_id = %s AND w.status = 'waiting'
            ORDER BY w.added_at ASC
            LIMIT 1
            """,
            (event_id,),
        )
        waitlist_user = cursor.fetchone()

        if not waitlist_user:
            cursor.close()
            return {"success": False, "message": "No users on the waitlist"}

        # Simulate sending a notification
        print(f"Notifying user {waitlist_user['email']} about an open spot in event {event_id}")

        # Update waitlist status to 'notified'
        cursor.execute(
            """
            UPDATE waitlist
            SET status = 'notified'
            WHERE id = %s
            """,
            (waitlist_user["id"],),
        )
        db.commit()
        cursor.close()
        return {
            "success": True,
            "message": "User notified",
            "email": waitlist_user["email"],
        }


    @staticmethod
    def confirm_waitlist(event_id, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT * FROM waitlist
            WHERE event_id = %s AND user_id = %s AND status = 'notified'
            """,
            (event_id, user_id),
        )
        waitlist_entry = cursor.fetchone()

        if not waitlist_entry:
            cursor.close()
            return {"success": False, "message": "No notification found for this user"}

        # Register the user
        cursor.execute(
            """
            INSERT INTO registrations (event_id, user_id)
            VALUES (%s, %s)
            """,
            (event_id, user_id),
        )

        # Remove the user from the waitlist
        cursor.execute(
            """
            DELETE FROM waitlist
            WHERE id = %s
            """,
            (waitlist_entry["id"],),
        )
        db.commit()
        cursor.close()
        return {"success": True, "message": "Waitlist spot confirmed and registered"}


    @staticmethod
    def event_notification():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT e.id, e.activity_group_name, e.date, u.email
            FROM event e
            JOIN registrations r ON r.event_id = e.id 
            JOIN resident u ON r.user_id = u.resident_id
            WHERE e.date BETWEEN NOW() AND NOW() + INTERVAL '1 day'
            """
        )
        events = cursor.fetchall()

        for event in events:
            print(
                f"Sending notification to {event['email']} for event {event['activity_group_name']}"
            )
        
        cursor.close()


    @staticmethod
    def search_events(search_term, date, location):
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT e.id, e.activity_group_name, e.date, e.location_id
            FROM event e
            LEFT JOIN location l ON e.location_id = l.id
            WHERE 1=1
        """
        params = []

        if search_term:
            query += " AND e.activity_group_name ILIKE %s"
            params.append(f"%{search_term}%")
        if date:
            query += " AND e.date = %s"
            params.append(date)
        if location:
            query += (
                " AND (l.address ILIKE %s OR l.city ILIKE %s OR l.state ILIKE %s OR l.zip_code ILIKE %s)"
            )
            params.extend([f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%"])

        query += " ORDER BY e.date DESC"
        cursor.execute(query, params)
        events = cursor.fetchall()
        cursor.close()
        return events


    @staticmethod
    def get_waitlist(user_id, event_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT w.id, w.event_id, w.user_id
            FROM waitlist w
            JOIN event e ON e.id = w.event_id
            JOIN resident u ON u.resident_id = w.user_id
            WHERE w.event_id = %s AND w.user_id = %s
            """,
            (event_id, user_id),
        )
        waitlist = cursor.fetchall()
        cursor.close()
        return waitlist

