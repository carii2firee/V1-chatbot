# ============= Mode Selector =============
import re
import speech_recognition as sr

# Mode handler imports (adjust these to match your files)
from name_recognition import handle_name_recognition
from math_processor import handle_math_and_science_mode
from book_recommender import handle_book_recommendation
from budget_tracker import start_budget_tracking
from depression_checker import handle_depression_screening
from house_helper import handle_house_assistance
from casual_chat import handle_casual_chat
from language_mode import language_translation_mode
from reminder_manager import handle_reminder_mode
from gui_launcher import run_voice_assistant_gui

# ---------- Voice Input Utilities ----------

def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("🎙️ Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Listening for your command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("❌ Sorry, I didn't catch that. Please try again.")
    except sr.RequestError:
        print("❌ Speech recognition service unavailable. Check your internet connection.")
    return None

def get_input(prompt_text=""):
    """
    Voice input with text fallback.
    Tries voice input first; if it fails, falls back to keyboard input.
    """
    user_input = listen_for_command()
    if user_input is None:
        user_input = input(prompt_text).strip().lower()
    else:
        user_input = user_input.strip().lower()
    return user_input

# ---------- Mode Selector ----------

def mode_selector(user_name, memory_logger):
    while True:
        print("\n📋 Available Modes:")
        print("  1. 🤖 Name Recognition")
        print("  2. ➗ Math Processing")
        print("  3. 📚 Book Recommendations & Storytelling")
        print("  4. 💰 Budget Tracking + Financial Advice")
        print("  5. 🧠 Depression Screening")
        print("  6. 🏡 House Tidying & Smart Home Tips")
        print("  7. 💬 Casual Chat")
        print("  8. 🧠 Memory Log Viewer")
        print("  9. 🌍 Language & Translation Mode")
        print(" 10. ⏰ Task handler/Reminder Mode")
        print(" 11. 🪟 Launch GUI Voice Assistant (Casual Chat)")
        print("  0. EXIT THE MODE SELECTOR")

        mode_choice = get_input("\nEnter or say the number of the mode you want to activate (or 'exit' to quit): ")

        if mode_choice in ['exit', '0']:
            print("Goodbye! You are now leaving the mode...")
            memory_logger.log_interaction("Exited mode selector", "")
            break

        memory_logger.log_interaction(f"Selected mode: {mode_choice}", "")

        if mode_choice in ["1", "one"]:
            handle_name_recognition(user_name, memory_logger)
        elif mode_choice in ["2", "two"]:
            handle_math_and_science_mode(user_name, memory_logger)
        elif mode_choice in ["3", "three"]:
            handle_book_recommendation(user_name, memory_logger)
        elif mode_choice in ["4", "four"]:
            start_budget_tracking(user_name)
        elif mode_choice in ["5", "five"]:
            handle_depression_screening(user_name, memory_logger)
        elif mode_choice in ["6", "six"]:
            handle_house_assistance(user_name, memory_logger)
        elif mode_choice in ["7", "seven"]:
            handle_casual_chat(user_name, memory_logger)
        elif mode_choice in ["8", "eight"]:
            memory_logger.view_logs()
            memory_logger.log_interaction("Viewed memory log", "")
            input("\n🔍 Press Enter to return to the mode selector...")
        elif mode_choice in ["9", "nine"]:
            language_translation_mode(user_name, memory_logger)
        elif mode_choice in ["10", "ten"]:
            handle_reminder_mode(user_name, memory_logger)
        elif mode_choice in ["11", "eleven"]:
            print("🪟 Launching the Voice Assistant GUI...")
            run_voice_assistant_gui()
        else:
            print("❌ Invalid mode choice. Please try again.")