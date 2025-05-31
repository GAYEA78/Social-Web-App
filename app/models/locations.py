import os

from app.utils.database import get_db


class Location:
    def __init__(self, location_id, address, city, state, zip_code):
        self.location_id = location_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code

    @staticmethod
    def create(address, city, state, zip_code):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO location (address, city, state, zip_code)
               VALUES (?, ?, ?, ?)""",
            (address, city, state, zip_code),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get(location_id):
        db = get_db()
        location = db.execute(
            """SELECT * FROM location WHERE location_id = ?""", (location_id,)
        ).fetchone()

        if location is None:
            return None

        return Location(
            location_id=location["location_id"],
            address=location["address"],
            city=location["city"],
            state=location["state"],
            zip_code=location["zip_code"],
        )

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute("""SELECT * FROM location ORDER BY city, state""").fetchall()
        return [
            Location(
                location_id=row["location_id"],
                address=row["address"],
                city=row["city"],
                state=row["state"],
                zip_code=row["zip_code"],
            )
            for row in rows
        ]

    def update(self):
        db = get_db()
        db.execute(
            """UPDATE location
               SET address = ?,
                   city = ?,
                   state = ?,
                   zip_code = ?
               WHERE location_id = ?""",
            (self.address, self.city, self.state, self.zip_code, self.location_id),
        )
        db.commit()

    def delete(self):
        db = get_db()
        db.execute("DELETE FROM location WHERE location_id = ?", (self.location_id,))
        db.commit()

    @staticmethod
    def search(query):
        db = get_db()
        search_term = f"%{query}%"
        locations = db.execute(
            """SELECT * FROM location 
               WHERE address LIKE ? 
               OR city LIKE ? 
               OR state LIKE ?
               OR zip_code LIKE ?""",
            (search_term, search_term, search_term, search_term),
        ).fetchall()
        return locations

    def get_google_maps_embed_url(self):
        """Generate a Google Maps embed URL for the location."""
        query = f"{self.address}, {self.city}, {self.state}, {self.zip_code}"
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_MAPS_API_KEY")
        return (
            f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={query.replace(' ', '+')}"
        )
