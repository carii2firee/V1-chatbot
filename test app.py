import threading
from voice_reminder import VoiceReminderListener
from reminder_manager import ReminderManager
from memory_logger import MemoryLogger, BeliefModel

# Use a test user ID
USER_ID = "test_user"

# Create a memory logger (required by your system)
memory_logger = MemoryLogger(USER_ID, BeliefModel(USER_ID))

# Create a ReminderManager for this user
reminder_manager = ReminderManager(USER_ID)

# Start the voice listener in a background thread
listener = VoiceReminderListener(USER_ID, reminder_manager)
listener.start()

print("🎤 Voice listener starting. Say something like 'reminder Buy milk at 5pm'.")

# Keep the main thread alive so the listener keeps running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopping listener...")
    listener.stop()
