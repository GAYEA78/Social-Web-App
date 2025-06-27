from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.activity_groups import ActivityGroup
from app.models.events import Event
from app.models.locations import Location
from app.models.prerequisite import Prerequisite
from app.utils.database import get_db
from app.utils.decorators import admin_required
from app.utils.maps_manager import MapsManager

events_bp = Blueprint("events", __name__)
maps_manager = MapsManager()





@events_bp.route("/events")
def list_events():
    search_query = request.args.get("q", "").strip()
    events = Event.get_all(search_query=search_query)
    for event in events:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM registrations WHERE event_id = %s AND status = 'registered'",
            (event['id'],)
        )
        count = cursor.fetchone()[0]
        cursor.close()
        event['registered_count'] = count
        # Attach maps embed URL
        event['maps_embed'] = maps_manager.get_event_map(event['id'])
    return render_template("events/list.html", events=events, search_query=search_query)


@events_bp.route("/events/<int:event_id>")
def view_event(event_id):
    event = Event.get(event_id)
    if not event:
        flash("Event not found", "error")
        return redirect(url_for("events.list_events"))
    
    # Get maps embed URL
    event['maps_embed'] = maps_manager.get_event_map(event_id)
    
    is_registered = False
    is_waitlisted = False
    
    if current_user.is_authenticated:
        db = get_db()
        cursor = db.cursor()
        # Check registration status
        cursor.execute(
            """
            SELECT * FROM registrations
            WHERE event_id = %s AND user_id = %s
            """,
            (event_id, current_user.id)
        )
        registration = cursor.fetchone()
        
        if registration:
            is_registered = registration['status'] == 'registered'
        else:
            # Check waitlist status
            cursor.execute(
                """
                SELECT * FROM waitlist
                WHERE event_id = %s AND user_id = %s
                """,
                (event_id, current_user.id)
            )
            waitlist = cursor.fetchone()
            is_waitlisted = bool(waitlist)
        
        cursor.close()
    
    # Get prerequisites
    prerequisites = Prerequisite.get_prerequisites(event_id)
    
    return render_template(
        "events/view.html",
        event=event,
        prerequisites=prerequisites,
        is_registered=is_registered,
        is_waitlisted=is_waitlisted
    )



@events_bp.route("/events/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_event():
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        try:
            # Activity group: use manual entry if provided, else dropdown
            group_name = request.form.get('activity_group_name') or request.form.get('activity_group_name_select')
            if not group_name:
                raise Exception('Activity group is required')

            # Check if activity group exists, if not create it
            cursor.execute(
                "SELECT name FROM activity_group WHERE name = %s",
                (group_name,)
            )
            existing_group = cursor.fetchone()
            
            if not existing_group:
                cursor.execute(
                    """
                    INSERT INTO activity_group (
                        name, category, description, founding_date, website, email,
                        phone_number, social_media_links, is_active, total_members,
                        event_frequency, membership_fee, open_to_public, min_age
                    )
                    VALUES (%s, 'General', 'New activity group', NOW(), '', '', '', '', TRUE, 0, 'monthly', 0, TRUE, 18)
                    """,
                    (group_name,)
                )
                db.commit()

            # Location: check if exists, else insert
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            zip_code = request.form['zip_code']
            
            cursor.execute(
                """
                SELECT id FROM location
                WHERE address = %s AND city = %s AND state = %s AND zip_code = %s
                """,
                (address, city, state, zip_code)
            )
            location = cursor.fetchone()
            
            if location:
                location_id = location[0]
            else:
                cursor.execute(
                    "INSERT INTO location (address, city, state, zip_code) VALUES (%s, %s, %s, %s) RETURNING id",
                    (address, city, state, zip_code)
                )
                location_result = cursor.fetchone()
                if location_result is None:
                    raise Exception("Failed to insert location and retrieve ID.")
                location_id = location_result[0]
                db.commit()

            # Create event
            cursor.execute(
                """
                INSERT INTO event (
                    activity_group_name, date, max_participants, cost,
                    registration_required, registration_deadline, location_id, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (
                    group_name,
                    request.form['date'],
                    request.form.get('max_participants'),
                    request.form.get('cost', 0),
                    'registration_required' in request.form,
                    request.form.get('registration_deadline'),
                    location_id,
                    current_user.id
                )
            )
            event_result = cursor.fetchone()
            if event_result is None:
                raise Exception("Failed to insert event and retrieve ID.")
            event_id = event_result[0]
            db.commit()

            # Store maps embed URL if provided
            maps_embed = request.form.get('maps_embed')
            if maps_embed:
                maps_manager.set_event_map(event_id, maps_embed)

            flash("Event created successfully", "success")
            return redirect(url_for("events.list_events"))
        except Exception as e:
            db.rollback()
            flash(f"Error creating event: {str(e)}", "error")
        finally:
            cursor.close()

    # GET: fetch activity groups for dropdown
    cursor = db.cursor()
    cursor.execute("SELECT name FROM activity_group")
    activity_groups = cursor.fetchall()
    cursor.close()
    return render_template("events/create.html", activity_groups=activity_groups)




@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.get(event_id)
    if not event:
        flash("Event not found", "error")
        return redirect(url_for("events.list_events"))

    if request.method == "POST":
        try:
            Event.update(
                event_id,
                activity_group_name=request.form['activity_group_name'],
                date=request.form['date'],
                max_participants=request.form.get('max_participants'),
                cost=request.form.get('cost', 0),
                registration_required='registration_required' in request.form,
                registration_deadline=request.form.get('registration_deadline'),
                location_id=request.form.get('location_id')
            )

            # Update maps embed URL if provided
            maps_embed = request.form.get('maps_embed')
            if maps_embed:
                maps_manager.set_event_map(event_id, maps_embed)
            else:
                maps_manager.remove_event_map(event_id)

            flash("Event updated successfully", "success")
            return redirect(url_for("events.view_event", event_id=event_id))
        except Exception as e:
            flash(f"Error updating event: {str(e)}", "error")

    # Get current maps embed URL
    event['maps_embed'] = maps_manager.get_event_map(event_id)
    return render_template("events/edit.html", event=event)


@events_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_event(event_id):
    try:
        Event.delete(event_id)
        flash("Event deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting event: {str(e)}", "error")

    return redirect(url_for("events.list_events"))


@events_bp.route("/events/<int:event_id>/register", methods=["POST"])
@login_required
def register_for_event(event_id):
    try:
        # Check prerequisites
        meets_prerequisites, unmet_prerequisites = Prerequisite.check_prerequisites(
            current_user.id, event_id
        )

        if not meets_prerequisites:
            flash("You do not meet the prerequisites for this event", "error")
            return redirect(url_for("events.view_event", event_id=event_id))

        # Register user
        registered = Event.register_user(event_id, current_user.id)

        if registered:
            flash("Successfully registered for event", "success")
        else:
            flash("Event is full. You have been added to the waitlist", "info")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error registering for event: {str(e)}", "error")

    return redirect(url_for("events.view_event", event_id=event_id))


@events_bp.route("/events/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel_registration(event_id):
    try:
        Event.cancel_registration(event_id, current_user.id)
        flash("Registration cancelled successfully", "success")
    except Exception as e:
        flash(f"Error cancelling registration: {str(e)}", "error")

    return redirect(url_for("events.view_event", event_id=event_id))


@events_bp.route("/events/<int:event_id>/notify-waitlist", methods=["POST"])
@login_required
@admin_required
def notify_waitlist(event_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT w.*, u.email
            FROM waitlist w
            JOIN resident u ON w.user_id = u.resident_id
            WHERE w.event_id = %s
            ORDER BY w.created_at ASC
            LIMIT 1
            """,
            (event_id,),
        )
        waitlisted = cursor.fetchone()
        cursor.close()

        if waitlisted:
            # TODO: Send email notification here.
            flash("Notification sent to next person on waitlist", "success")
        else:
            flash("No one is on the waitlist", "info")

    except Exception as e:
        flash(f"Error notifying waitlist: {str(e)}", "error")

    return redirect(url_for("events.view_event", event_id=event_id))
