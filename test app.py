# test_reminders.py
from voice_reminder import VoiceReminderListener
from reminder_manager import ReminderManager
import time

# ------------------ Setup ------------------
USER_ID = "user1"

# Initialize reminder manager
reminder_manager = ReminderManager(USER_ID)

# Initialize voice reminder listener
voice_listener = VoiceReminderListener(user_id=USER_ID, reminder_manager=reminder_manager)

# ------------------ Simulated Commands ------------------

# This function mimics what the listener would do if you spoke
def simulate_command(command_text: str):
    print(f"[User says] {command_text}")
    # Strip "WREN" prefix if present (like listener does)
    if "wren" in command_text.lower():
        command_text = command_text.lower().split("wren", 1)[1].strip()
    cmd, arg = voice_listener.parse_command(command_text)
    voice_listener.execute_command(cmd, arg)
    print("-" * 40)

# ------------------ Run Simulation ------------------

simulate_command("WREN remind me to buy milk at 5pm")
time.sleep(0.5)  # short delay to simulate time between commands
simulate_command("WREN remind me to call Alice tomorrow")
time.sleep(0.5)
simulate_command("WREN show my reminders")
time.sleep(0.5)
simulate_command("WREN check reminders")
time.sleep(0.5)
simulate_command("WREN clear reminders")
time.sleep(0.5)
simulate_command("WREN show my reminders")

print("\n✅ Hard-coded voice test complete.")
