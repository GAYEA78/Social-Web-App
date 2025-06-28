from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel

from app.utils.database import get_db

class StrEnum(str, Enum):
    pass


class EventFrequency(StrEnum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class ActivityGroup(BaseModel):
    name: str
    category: str
    description: str
    founding_date: Optional[date]
    website: str
    email: Optional[str]
    phone_number: str
    social_media_links: str  
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

        result = []
        for group in groups:
            fd = group["founding_date"]
            if isinstance(fd, str):
                try:
                    fd = datetime.strptime(fd, "%Y-%m-%d").date()
                except ValueError:
                    fd = None
            elif not isinstance(fd, date):
                fd = None

            ag = ActivityGroup(
                name=group["name"],
                category=group["category"],
                description=group["description"],
                founding_date=fd,
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
            result.append(ag)

        return result

    @staticmethod
    def get(name):  
        db = get_db()
        group = db.execute("""SELECT * FROM activity_group WHERE name = %s""", (name,)).fetchone()

        if group is None:
            return None

        fd = group["founding_date"]
        if isinstance(fd, str):
            try:
                fd = datetime.strptime(fd, "%Y-%m-%d").date()
            except ValueError:
                fd = None
        elif not isinstance(fd, date):
            fd = None

        return ActivityGroup(
            name=group["name"],
            category=group["category"],
            description=group["description"],
            founding_date=fd,
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
