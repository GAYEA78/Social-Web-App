from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.member import Member

members_bp = Blueprint("members", __name__)


@members_bp.route("/members/<string:activity_group_name>")
@login_required
def list_members(activity_group_name):
    members = Member.get_members(activity_group_name)
    return render_template(
        "members/list.html", members=members, activity_group_name=activity_group_name
    )


@members_bp.route("/members/add", methods=["POST"])
@login_required
def add_member():
    resident_id = request.form["resident_id"]
    activity_group_name = request.form["activity_group_name"]
    join_date = request.form["join_date"]
    role = request.form["role"]

    try:
        Member.add_member(resident_id, activity_group_name, join_date, role)
        flash("Member added successfully", "success")
    except Exception as e:
        flash(f"Error adding member: {str(e)}", "error")

    return redirect(url_for("members.list_members", activity_group_name=activity_group_name))


@members_bp.route("/members/remove", methods=["POST"])
@login_required
def remove_member():
    resident_id = request.form["resident_id"]
    activity_group_name = request.form["activity_group_name"]

    try:
        Member.remove_member(resident_id, activity_group_name)
        flash("Member removed successfully", "success")
    except Exception as e:
        flash(f"Error removing member: {str(e)}", "error")

    return redirect(url_for("members.list_members", activity_group_name=activity_group_name))
