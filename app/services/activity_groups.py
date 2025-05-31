import re

from app.models.activity_groups import ActivityGroup
from app.utils.database import get_db


class ActivityGroupsService:
    def __init__(self):
        self.cursor = get_db().cursor()
        self.columns = list(ActivityGroup.model_fields.keys())

    def get_all_activity_groups(self) -> list[ActivityGroup]:
        self.cursor.execute("SELECT * FROM activity_group")
        rows = self.cursor.fetchall()
        activity_groups: list[ActivityGroup] = [
            ActivityGroup.model_validate(dict(zip(self.columns, row))) for row in rows
        ]
        return activity_groups

    def search_activity_groups(self, pattern: str) -> list[ActivityGroup]:
        """
        Return all ActivityGroup whose name or category matches
        the given regex pattern (case-insensitive).
        """
        self.cursor.execute("SELECT * FROM activity_group")
        rows = self.cursor.fetchall()

        prog = re.compile(pattern, re.IGNORECASE)
        matches = []
        for row in rows:
            data = dict(zip(self.columns, row))
            if prog.search(data["name"]) or prog.search(data["category"]):
                matches.append(ActivityGroup.model_validate(data))
        return matches
