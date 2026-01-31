import os
import json
from datetime import datetime
import dateparser

class ReminderManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.file_path = f"{self.user_id}_reminders.json"
        self.reminders = []
        if os.path.exists(self.file_path):
            self.load_from_file()
        else:
            self._save([])

    # --- Internal helpers ---
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self):
        self.reminders = self._load() or []

    # --- Public methods ---
    def add_reminder(self, text, due_time=None):
        if isinstance(due_time, str):
            parsed_time = dateparser.parse(due_time, settings={"PREFER_DATES_FROM": "future"})
            if not parsed_time:
                return {"success": False, "response": "⚠️ Could not understand the time."}
            due_time = parsed_time

        if not due_time:
            due_time = datetime.now()

        reminder = {
            "reminder": text,
            "added_at": datetime.now().isoformat(),
            "due_time": due_time.isoformat()
        }
        self.reminders.append(reminder)
        self._save(self.reminders)

        return {"success": True, "response": f"✅ Reminder added: {text} at {due_time}"}

    def view_reminders(self):
        self.load_from_file()
        if not self.reminders:
            return {"success": True, "response": "🔕 No reminders saved.", "tasks": []}
        return {"success": True, "response": f"📋 Reminders ({len(self.reminders)})", "tasks": self.reminders}

    def check_due_reminders(self):
        self.load_from_file()
        now = datetime.now()
        due = []
        for r in self.reminders:
            t = datetime.fromisoformat(r["due_time"])
            if t <= now:
                due.append(r)
        response = (
            f"⏰ {len(due)} reminder(s) are due now." if due else "✅ No reminders are due right now."
        )
        return {"success": True, "response": response, "tasks": due}

    def clear_reminders(self):
        self.reminders = []
        self._save(self.reminders)
        return {"success": True, "response": "✅ All reminders cleared.", "tasks": []}
