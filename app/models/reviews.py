from app.utils.database import get_db

class Review:
    def __init__(
        self,
        review_id,
        resident_id,
        activity_group_name,
        content,
        star_rating,
        review_date,
        is_verified,
    ):
        self.review_id = review_id
        self.resident_id = resident_id
        self.activity_group_name = activity_group_name
        self.content = content
        self.star_rating = star_rating
        self.review_date = review_date
        self.is_verified = is_verified

    @staticmethod
    def create(
        resident_id,
        activity_group_name,
        content,
        star_rating,
        review_date,
        is_verified=False,
    ):
        if not (1 <= star_rating <= 5):
            raise ValueError("Star rating must be between 1 and 5")
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO review (resident_id, activity_group_name, content, 
                                   star_rating, review_date, is_verified)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING review_id""",
            (
                resident_id,
                activity_group_name,
                content,
                star_rating,
                review_date,
                is_verified,  # pass boolean, not int
            ),
        )
        review_id = cursor.fetchone()["review_id"]
        db.commit()
        cursor.close()
        return review_id

    @staticmethod
    def get(review_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT * FROM review WHERE review_id = %s""",
            (review_id,),
        )
        review = cursor.fetchone()
        cursor.close()

        if review is None:
            return None

        return Review(
            review_id=review["review_id"],
            resident_id=review["resident_id"],
            activity_group_name=review["activity_group_name"],
            content=review["content"],
            star_rating=review["star_rating"],
            review_date=review["review_date"],
            is_verified=review["is_verified"],
        )

    def update(self):
        if not (1 <= self.star_rating <= 5):
            raise ValueError("Star rating must be between 1 and 5")
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE review
               SET content = %s,
                   star_rating = %s,
                   review_date = %s,
                   is_verified = %s
               WHERE review_id = %s""",
            (
                self.content,
                self.star_rating,
                self.review_date,
                self.is_verified,
                self.review_id,
            ),
        )
        db.commit()
        cursor.close()

    def delete(self):
        """Hard delete the review from the database."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM review WHERE review_id = %s", (self.review_id,))
        db.commit()
        cursor.close()

    @staticmethod
    def get_by_activity_group(activity_group_name, page=1, per_page=10):
        """Fetch reviews for an activity group with pagination."""
        db = get_db()
        offset = (page - 1) * per_page
        cursor = db.cursor()
        cursor.execute(
            """SELECT r.*, u.username AS resident_name
               FROM review r
               JOIN resident u ON r.resident_id = u.resident_id
               WHERE r.activity_group_name = %s
               ORDER BY r.review_date DESC
               LIMIT %s OFFSET %s""",
            (activity_group_name, per_page, offset),
        )
        reviews = cursor.fetchall()
        cursor.close()
        return [dict(review) for review in reviews]

    @staticmethod
    def get_by_resident(resident_id, page=1, per_page=10):
        """Fetch reviews by a resident with pagination."""
        db = get_db()
        offset = (page - 1) * per_page
        cursor = db.cursor()
        cursor.execute(
            """SELECT r.*, ag.name AS activity_group_name
               FROM review r
               JOIN activity_group ag ON r.activity_group_name = ag.name
               WHERE r.resident_id = %s
               ORDER BY r.review_date DESC
               LIMIT %s OFFSET %s""",
            (resident_id, per_page, offset),
        )
        reviews = cursor.fetchall()
        cursor.close()
        return [dict(review) for review in reviews]

    @staticmethod
    def get_average_rating(activity_group_name):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT AVG(star_rating) AS avg_rating
               FROM review
               WHERE activity_group_name = %s""",
            (activity_group_name,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result["avg_rating"] if result and result["avg_rating"] is not None else 0
