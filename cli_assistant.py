
# ============== Main Execution ===============

import re
from voice_input import get_input  # Your voice + fallback input function
from reminder_manager import ReminderManager
from belief_system import BeliefModel
from memory_logger import MemoryLogger
from mode_selector import mode_selector


def sanitize_username(name: str) -> str:
    """Remove unwanted chars, keep only alphanumeric and underscore."""
    return re.sub(r'[^a-zA-Z0-9_]', '', name)

def run_cli_assistant():
    print("👋 Hello, I am your personal AI companion!")
    print("💡 Fun fact: AI stands for Artificial Intelligence.\n")

    # Get username with voice input + fallback
    user_name_raw = get_input("📝 Enter your name here: ").strip()
    user_name = sanitize_username(user_name_raw) or "user"

    print(f"\nNice to meet you, {user_name}! How can I help you today?")
    print("💡 Say or type 'modes' to see what I can do, or 'bye' to exit.\n")

    # Initialize your modules
    reminder_manager = ReminderManager(user_name)
    reminder_manager.view_reminders()
    belief_model = BeliefModel(user_name)
    memory_logger = MemoryLogger(user_name, belief_model)

    while True:
        user_input = get_input("Say or type your command: ").strip().lower()

        modes_triggers = {
            "modes",
            "bring me to the modes",
            "go to modes",
            "take me to the modes",
            "take me to the mode selector",
            "i request the mode selector"
        }

        if user_input in modes_triggers:
            print("\n📋 Available Modes:")
            print("  1. 🤖 Name Recognition")
            print("  2. 🖊️ Subject + Math processing mode")
            print("  3. 📚 Book Recommendations & Storytelling")
            print("  4. 💰 Budget Tracking + Financial Advice")
            print("  5. 🧠 Depression Screening")
            print("  6. 🏡 House Tidying & Smart Home Tips")
            print("  7. 💬 Casual Chat")
            print("  8. 🧠 Memory Log Viewer")
            print("  9. 🌍 Language & Translation Mode")
            print(" 10. ⏰ Task Handler / Reminder Mode")
            print(" 11. 🪟 Launch GUI Voice Assistant (Casual Chat)")
            print("  0. 🚪 Exit the Mode Selector\n")

            memory_logger.log_interaction(user_input, "Viewed modes and entered mode selector")
            mode_selector(user_name, memory_logger)

        elif user_input == "bye":
            farewell = f"Goodbye {user_name}! Have a great day!"
            print(f"Chatbot: {farewell}")
            memory_logger.log_interaction(user_input, farewell)
            break

        else:
            response = "❌ Sorry, please say or type 'modes' to open the mode selector or 'bye' to exit."
            print(f"Chatbot: {response}")
            memory_logger.log_interaction(user_input, response)