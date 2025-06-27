import re

from app.models.activity_groups import ActivityGroup
from app.utils.database import get_db


class ActivityGroupsService:
    def __init__(self):
        self.cursor = get_db().cursor()

    def get_all_activity_groups(self) -> list[ActivityGroup]:
        self.cursor.execute("SELECT * FROM activity_group")
        rows = self.cursor.fetchall()
        activity_groups: list[ActivityGroup] = [
            ActivityGroup.model_validate(row) for row in rows
        ]
        return activity_groups

    def search_activity_groups(self, pattern: str) -> list[ActivityGroup]:
        self.cursor.execute("SELECT * FROM activity_group")
        rows = self.cursor.fetchall()

        prog = re.compile(pattern, re.IGNORECASE)
        matches = []
        for row in rows:
            if prog.search(row["name"]) or prog.search(row["category"]):
                matches.append(ActivityGroup.model_validate(row))
        return matches
