import os
import json
from datetime import datetime
from voice_input import get_input  # your voice + fallback input function

class ReminderManager:
    def __init__(self, user_name):
        self.file_path = f"{user_name}_reminders.json"
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def add_reminder(self, reminder):
        with open(self.file_path, 'r+') as f:
            data = json.load(f)
            data.append({
                "reminder": reminder,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def view_reminders(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            if not data:
                print("🔕 No reminders saved.")
                return
            print("\n📌 Your Reminders:")
            for i, entry in enumerate(data, 1):
                print(f"{i}. {entry['reminder']} (added on {entry['timestamp']})")

    def clear_reminders(self):
        with open(self.file_path, 'w') as f:
            json.dump([], f)
        print("✅ All reminders cleared.")

def handle_reminder_mode(user_name, memory_logger=None):
    reminder_manager = ReminderManager(user_name)
    print("\n=== 🧠 Reminder Mode ===")

    while True:
        print("\nWhat would you like to do?")
        print("1. Add a reminder")
        print("2. View reminders")
        print("3. Clear all reminders")
        print("4. Exit reminder mode")

        choice = get_input("Say or type a number (1-4): ").strip().lower()

        spoken_map = {"one": "1", "two": "2", "three": "3", "four": "4"}
        choice = spoken_map.get(choice, choice)

        if choice == "1":
            reminder = get_input("What's the reminder? ").strip()
            if reminder:
                reminder_manager.add_reminder(reminder)
                print("📝 Reminder saved!")
                if memory_logger:
                    memory_logger.log_interaction("Added reminder", reminder)
            else:
                print("❌ Reminder cannot be empty.")

        elif choice == "2":
            reminder_manager.view_reminders()
            if memory_logger:
                memory_logger.log_interaction("Viewed reminders", "")

        elif choice == "3":
            confirm = get_input("Are you sure? This will delete all reminders. Say 'yes' or 'no': ").strip().lower()
            if confirm in ["yes", "y"]:
                reminder_manager.clear_reminders()
                if memory_logger:
                    memory_logger.log_interaction("Cleared reminders", "")
            else:
                print("❌ Clear canceled.")

        elif choice == "4":
            print("📤 Exiting Reminder Mode...")
            if memory_logger:
                memory_logger.log_interaction("Exited Reminder Mode", "")
            break

        else:
            print("❌ Invalid choice. Please select 1-4.")