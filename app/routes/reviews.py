from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.reviews import Review

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/activity-group/<name>/reviews")
def list_reviews(name):
    """Display all reviews for an activity group."""
    reviews = Review.get_by_activity_group(name)
    avg_rating = Review.get_average_rating(name)
    return render_template(
        "reviews/list.html",
        activity_group_name=name,
        reviews=reviews,
        avg_rating=avg_rating,
    )


@reviews_bp.route("/activity-group/<name>/review/new", methods=["GET", "POST"])
@login_required
def create_review(name):
    """Create a new review for an activity group."""
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        try:
            star_rating = int(request.form.get("star_rating", 0))
            if not 1 <= star_rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            flash("Invalid star rating", "error")
            return redirect(url_for("reviews.create_review", name=name))

        if not content:
            flash("Review content cannot be empty", "error")
            return redirect(url_for("reviews.create_review", name=name))

        Review.create(
            resident_id=current_user.id,
            activity_group_name=name,
            content=content,
            star_rating=star_rating,
            review_date=datetime.now().strftime("%Y-%m-%d"),
        )
        flash("Review submitted successfully!", "success")
        return redirect(url_for("reviews.list_reviews", name=name))

    return render_template("reviews/create.html", activity_group_name=name)


@reviews_bp.route("/review/<int:review_id>/edit", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    """Edit an existing review."""
    review = Review.get(review_id)
    if not review:
        flash("Review not found", "error")
        return redirect(url_for("main.index"))

    if review.resident_id != current_user.id:
        flash("You can only edit your own reviews", "error")
        return redirect(url_for("reviews.list_reviews", name=review.activity_group_name))

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        try:
            star_rating = int(request.form.get("star_rating", 0))
            if not 1 <= star_rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            flash("Invalid star rating", "error")
            return redirect(url_for("reviews.edit_review", review_id=review_id))

        if not content:
            flash("Review content cannot be empty", "error")
            return redirect(url_for("reviews.edit_review", review_id=review_id))

        review.content = content
        review.star_rating = star_rating
        review.update()
        flash("Review updated successfully!", "success")
        return redirect(url_for("reviews.list_reviews", name=review.activity_group_name))

    return render_template(
        "reviews/edit.html",
        review=review,
        activity_group_name=review.activity_group_name,
    )


@reviews_bp.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    """Soft delete a review."""
    review = Review.get(review_id)
    if not review:
        flash("Review not found", "error")
        return redirect(url_for("main.index"))

    if review.resident_id != current_user.id:
        flash("You can only delete your own reviews", "error")
        return redirect(url_for("reviews.list_reviews", name=review.activity_group_name))

    review.delete()  # Use hard delete instead of soft delete
    flash("Review deleted successfully!", "success")
    return redirect(url_for("reviews.list_reviews", name=review.activity_group_name))
