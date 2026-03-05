import os
import json
from datetime import datetime, timedelta
import dateparser


class ReminderManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.file_path = f"{self.user_id}_reminders.json"
        self.reminders = self._load()  # load directly

    # --- Internal helper methods ---
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        else:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.reminders, f, indent=4)

    # --- Public methods ---
    def add_reminder(self, text, due_time=None):
        """
        Add a new reminder. Supports optional due_time string from JS payload.
        If no due_time is provided, sets reminder 30 minutes from now.
        Accepts exact times like '5 pm' and calculates the correct future datetime.
        """

        # --- Extract due_time from JS payload if present ---
        if '|' in text:
            text, due_time_str = text.split('|', 1)
            due_time = dateparser.parse(due_time_str, settings={"PREFER_DATES_FROM": "future"})

        # --- Parse natural language due_time string if still a string ---
        if isinstance(due_time, str):
            due_time = dateparser.parse(due_time, settings={"PREFER_DATES_FROM": "future"})

        now = datetime.now()

        # --- Default to 30 minutes from now if no valid due_time ---
        if not due_time:
            due_time = now + timedelta(minutes=30)
        else:
            # If user entered a time like "5 pm", calculate exact future datetime
            # dateparser already returns future date if possible, but ensure it's not in the past
            if due_time <= now:
                # If the parsed time is earlier than now, move it to next day
                due_time += timedelta(days=1)

        # --- Store reminder ---
        reminder = {
            "text": text.strip(),
            "scheduled_time": due_time.isoformat()
        }
        self.reminders.append(reminder)
        self._save()

        return {
            "success": True,
            "response": f"✅ Reminder added: {text.strip()} at {due_time.strftime('%Y-%m-%d %I:%M %p')}"
        }

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
        return {"success": True, "response": "✅ All reminders have been successfully cleared.", "tasks": []}
