from flask import Blueprint, render_template, request
from flask_login import current_user
from app.services.activity_groups import ActivityGroupsService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main landing page with optional category search."""
    svc = ActivityGroupsService()
    q = (request.args.get("category") or "").strip()
    if q:
        activity_groups = svc.search_activity_groups(q)
    else:
        activity_groups = svc.get_all_activity_groups()
    return render_template(
        "main/index.html", all_activity_groups=activity_groups, search_category=q
    )
