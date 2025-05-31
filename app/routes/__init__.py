from flask import Flask, Blueprint, render_template
from flask_login import login_required, current_user

from app.routes.auth import auth_bp
from app.routes.events import events_bp
from app.routes.main import main_bp
from app.routes.members import members_bp
from app.routes.prerequisites import prerequisites_bp
from app.routes.reviews import reviews_bp
from app.routes.sessions import sessions_bp

from app.models.events import Event
from app.utils.database import get_db


def init_app(app: Flask):
    """Initialize all blueprints with the app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(prerequisites_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(members_bp)

@main_bp.route('/profile')
@login_required
def profile():
    db = get_db()
    if current_user.is_admin:
        # Events created by this admin
        created_events = db.execute(
            '''SELECT e.id, e.activity_group_name, e.date,
                      (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'registered') as registered_count,
                      (SELECT COUNT(*) FROM waitlist w WHERE w.event_id = e.id) as waitlist_count
               FROM event e
               WHERE e.created_by = ?''',
            (current_user.id,)
        ).fetchall()
        # For each event, fetch registered and waitlisted users
        event_user_info = {}
        for event in created_events:
            registered = db.execute(
                '''SELECT u.resident_id, u.username, u.email, r.created_at, r.status
                   FROM registrations r
                   JOIN resident u ON r.user_id = u.resident_id
                   WHERE r.event_id = ? AND r.status = 'registered' ''',
                (event['id'],)
            ).fetchall()
            waitlisted = db.execute(
                '''SELECT u.resident_id, u.username, u.email, w.created_at
                   FROM waitlist w
                   JOIN resident u ON w.user_id = u.resident_id
                   WHERE w.event_id = ?''',
                (event['id'],)
            ).fetchall()
            event_user_info[event['id']] = {
                'registered': registered,
                'waitlisted': waitlisted
            }
        return render_template('admin_dashboard.html', created_events=created_events, event_user_info=event_user_info)
    else:
        # Registered events
        registered_events = db.execute(
            '''SELECT e.id, e.activity_group_name, e.date
               FROM event e
               JOIN registrations r ON r.event_id = e.id
               WHERE r.user_id = ? AND r.status = 'registered' ''',
            (current_user.id,)
        ).fetchall()
        # Waitlisted events
        waitlisted_events = db.execute(
            '''SELECT e.id, e.activity_group_name, e.date
               FROM event e
               JOIN waitlist w ON w.event_id = e.id
               WHERE w.user_id = ?''',
            (current_user.id,)
        ).fetchall()
        return render_template('profile.html', registered_events=registered_events, waitlisted_events=waitlisted_events)
