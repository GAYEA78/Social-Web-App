import json
import os
import re
from pathlib import Path

class MapsManager:
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / 'data' / 'maps_data.json'
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Ensure the data file and directory exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            with open(self.data_file, 'w') as f:
                json.dump({"event_maps": {}}, f)

    def get_maps_data(self):
        """Read the maps data from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"event_maps": {}}

    def save_maps_data(self, data):
        """Save the maps data to the JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def get_event_map(self, event_id):
        """Get the maps embed URL for a specific event."""
        data = self.get_maps_data()
        return data["event_maps"].get(str(event_id))

    def set_event_map(self, event_id, maps_embed_url):
        """Set the maps embed URL for a specific event, validating the input."""
        url = self.extract_url(maps_embed_url)
        data = self.get_maps_data()
        data["event_maps"][str(event_id)] = url
        self.save_maps_data(data)

    def remove_event_map(self, event_id):
        """Remove the maps embed URL for a specific event."""
        data = self.get_maps_data()
        if str(event_id) in data["event_maps"]:
            del data["event_maps"][str(event_id)]
            self.save_maps_data(data)

    @staticmethod
    def extract_url(embed_code):
        """Extracts the src URL from an iframe or returns the string if it's already a URL."""
        if not embed_code:
            return ''
        # If it's already a URL
        if embed_code.strip().startswith('http'):
            return embed_code.strip()
        # Try to extract src from iframe
        match = re.search(r'src=["\"](.*?)["\"]', embed_code)
        if match:
            return match.group(1)
        return embed_code.strip() 