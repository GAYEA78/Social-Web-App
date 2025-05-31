from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.events import Event
from app.models.sessions import Session

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions")
def list_sessions():
    sessions = Session.get_all()
    return render_template("sessions/list.html", sessions=sessions)


@sessions_bp.route("/sessions/<int:session_id>")
def view_session(session_id):
    session = Session.get(session_id)
    if session is None:
        flash("Session not found", "error")
        return redirect(url_for("sessions.list_sessions"))

    return render_template("sessions/view.html", session=session)


@sessions_bp.route("/sessions/create", methods=["GET", "POST"])
@login_required
def create_session():
    if request.method == "POST":
        activity_group_name = request.form["activity_group_name"]
        event_id = request.form["event_id"]
        date = request.form["date"]
        attendance = request.form.get("attendance", type=int)
        agenda = request.form["agenda"]

        # Validate the data
        if not activity_group_name or not event_id or not date:
            flash("Activity group name, event, and date are required", "error")
            return redirect(url_for("sessions.create_session"))

        try:
            session_id = Session.create(
                activity_group_name=activity_group_name,
                event_id=event_id,
                date=date,
                attendance=attendance,
                agenda=agenda,
            )
            flash("Session created successfully", "success")
            return redirect(url_for("sessions.view_session", session_id=session_id))
        except Exception as e:
            flash(f"Error creating session: {str(e)}", "error")
            return redirect(url_for("sessions.create_session"))

    # GET request - show the create form
    events = Event.get_all()
    return render_template("sessions/create.html", events=events)


@sessions_bp.route("/sessions/<int:session_id>/edit", methods=["GET", "POST"])
@login_required
def edit_session(session_id):
    session = Session.get(session_id)
    if session is None:
        flash("Session not found", "error")
        return redirect(url_for("sessions.list_sessions"))

    if request.method == "POST":
        session.activity_group_name = request.form["activity_group_name"]
        session.event_id = request.form["event_id"]
        session.date = request.form["date"]
        session.attendance = request.form.get("attendance", type=int)
        session.agenda = request.form["agenda"]

        try:
            session.update()
            flash("Session updated successfully", "success")
            return redirect(url_for("sessions.view_session", session_id=session_id))
        except Exception as e:
            flash(f"Error updating session: {str(e)}", "error")

    events = Event.get_all()
    return render_template("sessions/edit.html", session=session, events=events)


@sessions_bp.route("/sessions/<int:session_id>/delete", methods=["POST"])
@login_required
def delete_session(session_id):
    session = Session.get(session_id)
    if session is None:
        flash("Session not found", "error")
    else:
        try:
            session.soft_delete()  # Use soft_delete instead of delete
            flash("Session deleted successfully", "success")
        except Exception as e:
            flash(f"Error deleting session: {str(e)}", "error")

    return redirect(url_for("sessions.list_sessions"))
