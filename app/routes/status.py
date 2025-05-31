from datetime import datetime

from flask import Blueprint, jsonify

status_bp = Blueprint("status", __name__)


@status_bp.route("/")
def health_check():
    """Basic health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "project-1-online-commerce",
        }
    )
