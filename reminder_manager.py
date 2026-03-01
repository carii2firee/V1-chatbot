import os
import json
from datetime import datetime
import dateparser


class ReminderManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.file_path = f"{self.user_id}_reminders.json"
        self.reminders = self._load()  # load directly, no extra check

    # --- Internal helper methods ---
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        else:
            # Initialize empty file if not exist
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def _save(self):
        # Save self.reminders only (no extra data passed)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.reminders, f, indent=4)

    # --- Public methods ---
    def add_reminder(self, text, due_time=None):
        """Add a new reminder. Parse natural language time if string."""
        if isinstance(due_time, str):
            due_time = dateparser.parse(due_time, settings={"PREFER_DATES_FROM": "future"})
            if not due_time:
                return {"success": False, "response": "⚠️ Could not understand the time."}

        if not due_time:
            due_time = datetime.now()

        # Store as ISO and immediately persist
        reminder = {"text": text, "scheduled_time": due_time.isoformat()}
        self.reminders.append(reminder)
        self._save()

        return {"success": True, "response": f"✅ Reminder added: {text} at {due_time}"}

    def view_reminders(self):
        """Return all reminders sorted by due time."""
        self.reminders.sort(key=lambda r: r["scheduled_time"])
        if not self.reminders:
            return {"success": True, "response": "🔕 No reminders saved.", "tasks": []}
        return {"success": True, "response": f"📋 Reminders ({len(self.reminders)})", "tasks": self.reminders}

    def check_due_reminders(self):
        """Return reminders that are due now."""
        now = datetime.now()
        due = []
        for r in self.reminders:
            try:
                t = datetime.fromisoformat(r["scheduled_time"])
                if t <= now:
                    due.append(r)
            except Exception:
                continue  # skip malformed dates

        response = f"⏰ {len(due)} reminder(s) are due now." if due else "✅ No reminders are due right now."
        return {"success": True, "response": response, "tasks": due}

    def clear_reminders(self):
        """Delete all reminders."""
        self.reminders = []
        self._save()
        return {"success": True, "response": "✅ All reminders cleared.", "tasks": []}
