from flask import Blueprint, render_template

from app.models.locations import Location

locations_bp = Blueprint("locations", __name__)


@locations_bp.route("/locations/<int:location_id>")
def location_details(location_id):
    location = Location.get(location_id)
    if not location:
        return "Location not found", 404
    return render_template("locations/details.html", location=location)
