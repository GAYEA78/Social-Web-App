from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from app.utils.database import get_db


class EventFrequency(StrEnum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class ActivityGroup(BaseModel):
    name: str
    category: str
    description: str
    founding_date: Optional[str]
    website: str
    email: Optional[str]
    phone_number: str
    social_media_links: str  # Json string
    is_active: bool
    total_members: int
    event_frequency: EventFrequency
    membership_fee: int
    open_to_public: bool
    min_age: int

    @staticmethod
    def get_all():
        db = get_db()
        groups = db.execute("""SELECT * FROM activity_group ORDER BY name""").fetchall()
        return groups

    @staticmethod
    def get(name):
        db = get_db()
        group = db.execute("""SELECT * FROM activity_group WHERE name = ?""", (name,)).fetchone()

        if group is None:
            return None

        return ActivityGroup(
            name=group["name"],
            category=group["category"],
            description=group["description"],
            founding_date=group["founding_date"],
            website=group["website"],
            email=group["email"],
            phone_number=group["phone_number"],
            social_media_links=group["social_media_links"],
            is_active=bool(group["is_active"]),
            total_members=group["total_members"],
            event_frequency=group["event_frequency"],
            membership_fee=group["membership_fee"],
            open_to_public=bool(group["open_to_public"]),
            min_age=group["min_age"],
        )
