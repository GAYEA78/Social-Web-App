from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.events import Event
from app.models.prerequisite import Prerequisite
from app.utils.decorators import admin_required

prerequisites_bp = Blueprint('prerequisites', __name__)

@prerequisites_bp.route('/events/<int:event_id>/prerequisites')
@login_required
@admin_required
def list_prerequisites(event_id):
    event = Event.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events.list_events'))
    
    prerequisites = Prerequisite.get_prerequisites(event_id)
    available_events = Event.get_all(exclude_event_id=event_id)
    
    return render_template('events/prerequisites.html',
                         event=event,
                         prerequisites=prerequisites,
                         available_events=available_events)

@prerequisites_bp.route('/events/<int:event_id>/prerequisites/add', methods=['POST'])
@login_required
@admin_required
def add_prerequisite(event_id):
    event = Event.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events.list_events'))
    
    prerequisite_event_id = request.form.get('prerequisite_event_id')
    minimum_performance = request.form.get('minimum_performance')
    qualification_period = request.form.get('qualification_period')
    is_waiver_allowed = 'is_waiver_allowed' in request.form
    
    if not all([prerequisite_event_id, minimum_performance, qualification_period]):
        flash('All fields are required', 'error')
        return redirect(url_for('prerequisites.list_prerequisites', event_id=event_id))
    
    try:
        Prerequisite.create(
            event_id=event_id,
            prerequisite_event_id=prerequisite_event_id,
            minimum_performance=int(minimum_performance),
            qualification_period=int(qualification_period),
            is_waiver_allowed=is_waiver_allowed
        )
        flash('Prerequisite added successfully', 'success')
    except Exception as e:
        flash(f'Error adding prerequisite: {str(e)}', 'error')
    
    return redirect(url_for('prerequisites.list_prerequisites', event_id=event_id))

@prerequisites_bp.route('/events/<int:event_id>/prerequisites/<int:prerequisite_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_prerequisite(event_id, prerequisite_id):
    event = Event.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events.list_events'))
    
    try:
        Prerequisite.remove(prerequisite_id)
        flash('Prerequisite removed successfully', 'success')
    except Exception as e:
        flash(f'Error removing prerequisite: {str(e)}', 'error')
    
    return redirect(url_for('prerequisites.list_prerequisites', event_id=event_id))
