import nltk
import random
import requests
import os
from xml.etree import ElementTree as ET
from flask import Flask, request, jsonify
import threading
import wolframalpha
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import json
import sys
from datetime import datetime 
from deep_translator import GoogleTranslator
from googletrans import Translator
from llama_cpp import Llama
load_dotenv()
datetime.now()


youtube_api_key = os.getenv('YT_IFYKYK')
WOLFRAM_API_KEY = os.getenv('WOLF_IFYKYK')
# ======= Translate_text function =========
def translate_text(text, target_lang):
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Error: {e}"
    

# ======== Check if my API keys are functional =========

if youtube_api_key:
    print("✅ YouTube API key loaded.")
else:
    print("❌ YouTube API key missing.")

if WOLFRAM_API_KEY:
    print("✅ Wolfram Alpha API key loaded.")
else:
    print("❌ Wolfram Alpha API key missing.")

# ============ Handler functions =======
def handle_name_recognition(user_name, memory_logger):
    print("\n=== Name Recognition System ===")
    name = input("Enter a name to check: ").strip()
    memory_logger.log_interaction(name, "")
    check_name(name)
    memory_logger.log_interaction(name, "Checked name recognition")

def handle_math_processing(user_name, memory_logger):
    print("\n=== Math Processing System ===")
    question = input("Enter any math question: ").strip()
    memory_logger.log_interaction(question, "")
    result = handle_math_question(question)
    print(f"Result: {result}")
    memory_logger.log_interaction(question, result)

def handle_book_recommendation(user_name, memory_logger):
    print("\n=== Book Recommendation and Storytelling Experience ===")
    topic = input("Enter a topic or genre (e.g., fantasy, science, adventure): ").strip()
    memory_logger.log_interaction(topic, "")
    if youtube_api_key:
        book_and_storytelling_experience(youtube_api_key)
    else:
        print("❌ YouTube API key not found.")
        memory_logger.log_interaction(topic, "YouTube API key missing")


def handle_depression_screening(user_name, memory_logger):
    print("\n=== Depression Screening ===")
    questions = [
        "Over the last two weeks, how often have you felt down, depressed, or hopeless?",
        "Have you had little interest or pleasure in doing things?",
        "Have you ever felt like hurting yourself or others?",
        "Does your life ever feel as if it doesn't matter?",
    ]

    options_text = (
        "Please answer each question with:\n"
        "1 = Very little or rarely\n"
        "2 = Not that much\n"
        "3 = This happens a lot\n"
    )
    print(options_text)

    total_score = 0
    for question in questions:
        while True:
            answer = input(f"{question}\nYour answer (1-3): ").strip()
            if answer in ('1', '2', '3'):
                answer_int = int(answer)
                total_score += answer_int
                memory_logger.log_interaction(question, answer_int)
                break
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

    print("\n=== Screening Results ===")
    if total_score <= 4:
        print("It seems you are experiencing very little to mild symptoms. Keep taking care of yourself!")
    elif 5 <= total_score <= 8:
        print("You might be experiencing some moderate symptoms. It could help to talk with someone you trust.")
    else:
        print("Your answers suggest more severe symptoms. Please consider reaching out to a mental health professional for support.")

    print("\nRemember, this screening is not a diagnosis. If you’re struggling, don’t hesitate to seek help.")

def handle_house_assistance(user_name, memory_logger):
    print("\n=== House Assistance ===")
    print("Available topics: cleaning, energy, security, organization, automation")
    topic = input("Enter a topic for house tidying advice: ").strip()
    memory_logger.log_interaction(topic, "")
    advice = house_tidying(topic)
    print(f"Advice: {advice}")
    memory_logger.log_interaction(topic, advice)

def handle_casual_chat(user_name, memory_logger):
    print("\n=== Casual Chat ===")
    memory_logger.log_interaction("Entered casual chat mode", "")
    casual_chat(user_name)
    memory_logger.log_interaction("Exited casual chat mode", "")


# === Reminder Manager === (same as before) ...
class ReminderManager:
    def __init__(self, user_name):
        self.user_name = user_name
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
    print("\n📬 Your current reminders (if any):")
    reminder_manager.view_reminders()

    while True:
        print("\nChoose an option:")
        print("1. Add a new reminder")
        print("2. View all reminders")
        print("3. Clear all reminders")
        print("4. Exit Reminder Mode")

        choice = input("Your choice: ").strip()

        if choice == "1":
            reminder = input("What would you like me to remember for you? ").strip()
            if reminder:
                reminder_manager.add_reminder(reminder)
                print("✅ Reminder added.")
                if memory_logger:
                    memory_logger.log_interaction("Added reminder", reminder)
            else:
                print("❌ Reminder cannot be empty.")

        elif choice == "2":
            reminder_manager.view_reminders()
            if memory_logger:
                memory_logger.log_interaction("Viewed reminders", "")

        elif choice == "3":
            confirm = input("Are you sure? This will delete all reminders. (yes/no): ").strip().lower()
            if confirm == "yes":
                reminder_manager.clear_reminders()
                if memory_logger:
                    memory_logger.log_interaction("Cleared reminders", "")
            else:
                print("❌ Clear canceled.")

        elif choice == "4":
            print("Exiting Reminder Mode...")
            if memory_logger:
                memory_logger.log_interaction("Exited Reminder Mode", "")
            break

        else:
            print("❌ Invalid input. Please choose 1–4.")

# === Language & Translation ===

user_language_preferences = {}
translator = Translator()


HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Or your preferred model endpoint

def generate_ai_response(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        # HuggingFace returns a list of generated texts, typically under 'generated_text'
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        else:
            # fallback: return the first text if any
            return data[0].get("generated_text", "").strip() if data else "Sorry, no response."
    except requests.exceptions.RequestException as e:
        print(f"❌ HuggingFace API error: {e}")
        return "Sorry, I couldn't generate a response right now."

def translate_text(text, target_lang_code):
    try:
        result = translator.translate(text, dest=target_lang_code)
        return result.text
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text
# =========== Language translation + switch languuage option ===========

translator = Translator()
llm = Llama(
    model_path="./llama.cpp/build/models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    n_ctx=512
)

class MemoryLogger:
    def __init__(self, user_name):
        self.user_name = user_name
        self.file_path = f"{user_name}_memory_log.json"
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def log_interaction(self, question, response):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "response": response
        }
        with open(self.file_path, 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)

    def view_log(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            if not data:
                print("Memory log is empty!")
                return
            print("\n--- Memory Log ---")
            for i, entry in enumerate(data):
                print(f"\n[{i+1}] {entry['timestamp']}")
                print(f"User: {entry['question']}")
                print(f"AI:   {entry['response']}")
            print("\n--- End of Log ---\n")


def language_translation_mode(user_name, memory_logger):
    translator = Translator()

    lang_examples = (
        "en - English, es - Spanish, fr - French, de - German, it - Italian, "
        "pt - Portuguese, ru - Russian, ja - Japanese, ko - Korean, zh-cn - Chinese (Simplified)"
    )

    print("Would you like to enable language translation for:")
    user_translate = input("1. Your inputs? (yes/no): ").strip().lower() in ("yes", "y")
    ai_translate = input("2. AI responses? (yes/no): ").strip().lower() in ("yes", "y")

    if not user_translate and not ai_translate:
        print("No translation enabled. Exiting.")
        return

    print("Here are some example language codes you can use:")
    print(lang_examples)

    target_lang = input("Enter the target language code (e.g., 'en', 'es', 'fr'): ").strip().lower()

    print("Translation mode active. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("Exiting translation mode.")
            break

        # Translate user input if enabled
        original_user_input = user_input
        if user_translate:
            try:
                user_input = translator.translate(user_input, dest=target_lang).text
                print(f"(Translated Input): {user_input}")
            except Exception as e:
                print(f"Error translating user input: {e}")

        # Simulate AI response (replace with real logic)
        ai_response = f"The translated version of that would be: '{user_input}'"

        # Translate AI response if enabled
        translated_response = ai_response
        if ai_translate:
            try:
                translated_response = translator.translate(ai_response, dest=target_lang).text
                print(f"AI: {translated_response}")
            except Exception as e:
                print(f"Error translating AI response: {e}")
        else:
            print(f"AI: {ai_response}")

        # Log original user input and final AI response
        memory_logger.log_interaction(original_user_input, translated_response)





#================================ Memory reminder function ==============================

class ReminderManager:
    def __init__(self, user_name):
        self.user_name = user_name
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
2.# 🔟 Add Mode 10 Handler
# Somewhere near your other handlers:

#python
#Copy
#Edit
def handle_reminder_mode(user_name, memory_logger):
    reminder_manager = ReminderManager(user_name)
    print("\n=== 🧠 Reminder Mode ===")

    while True:
        print("\nWhat would you like to do?")
        print("1. Add a reminder")
        print("2. View reminders")
        print("3. Clear all reminders")
        print("4. Exit reminder mode")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            reminder = input("What's the reminder? ").strip()
            reminder_manager.add_reminder(reminder)
            print("📝 Reminder saved!")
            memory_logger.log_interaction("Added reminder", reminder)

        elif choice == "2":
            reminder_manager.view_reminders()
            memory_logger.log_interaction("Viewed reminders", "")

        elif choice == "3":
            confirm = input("Are you sure? This will delete all reminders. (yes/no): ").strip().lower()
            if confirm == "yes":
                reminder_manager.clear_reminders()
                memory_logger.log_interaction("Cleared reminders", "")
            else:
                print("❌ Clear canceled.")

        elif choice == "4":
            print("Exiting Reminder Mode...")
            break

        else:
            print("❌ Invalid choice. Please select 1-4.")

# ========== Ensure safe gitignore ==============
def ensure_safe_gitignore():
    gitignore_path = '.gitignore'
    safe_ignore_content = """
    
    # Ignore environment variables
.env

# Ignore memory log files
*_memory_log.json

# Python cache
__pycache__/
*.pyc

# Logs
*.log

# VS Code setting
.vscode/
"""

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(safe_ignore_content.strip())
        print("✅ Created a safe .gitignore file.")
    else:
        print(".gitignore file already exists.")

# Call the function early in your main script or setup process
ensure_safe_gitignore()
 

youtube_api_key = os.getenv('YT_IFYKYK')
nltk.download('vader_lexicon')

# Configuration constants
WOLFRAM_API_KEY = os.getenv("WOLF_IFYKYK")
WOLFRAM_API_URL = "http://api.wolframalpha.com/v2/query"

# Initialize Flask app and Wolfram client
app = Flask(__name__)
wolfram_client = wolframalpha.Client(WOLFRAM_API_KEY)

# ============= NAME RECOGNITION SYSTEM =============
known_names = ["Shacarion Wrencher", "Juleena Pham", "Win Giang ", "Suri Situmorang"]

def check_name(user_name):
    if user_name in known_names:
        print(f"Chatbot: Hello, {user_name}, It's nice to see a familiar face, since you just told me your lovely name...")
    else:
        print(f"Chatbot: Nice to meet you, {user_name}, you look wonderful today!")



# ============= House Tidying Function (API Integration) =============
def house_tidying(topic):
    tips = {
        "cleaning": "Tip: Remember to take out the trash and do laundry. Oh, and one more thing: Check to see if there are dishes waiting for you. These are important tasks to maintain that cozy home feeling!",     
        "energy": "Tip: Make sure to turn off or unplug any electricity appliances throughout your home.",
        "security": "Tip: Install smart locks and motion-sensor lights for added security.",
        "organization": "Tip: Label storage bins and use vertical shelving to maximize space.",
        "automation": "Tip: Use a smart home hub to control lights and temperature efficiently."

    }
    return tips.get(topic.lower(), "I can help with cleaning, energy saving, security, organization, or automation tips!")




# ============= Math Processing System (Wolfram Alpha API Integration to allow for easier math processing) =============

def handle_math_question(question):
    try:
        params = {
            "input": question,
            "appid": WOLFRAM_API_KEY,
            "output": "XML",
            "podstate": "Step-by-step solution",  # request step-by-step if available
            "format": "plaintext"
        }
        response = requests.get(WOLFRAM_API_URL, params=params)
        response.raise_for_status()

        root = ET.fromstring(response.text)

        # To store sections of the response
        interpretation = None
        steps = []
        result = None

        for pod in root.findall(".//pod"):
            title = pod.get("title", "").lower()

            plaintext_elem = pod.find(".//plaintext")
            text = plaintext_elem.text if plaintext_elem is not None else None

            if not text:
                continue

            # Capture interpretation of the input
            if "input" in title and not interpretation:
                interpretation = text.strip()

            # Collect step-by-step solution(s)
            elif "step-by-step solution" in title or "steps" in title:
                steps.append(text.strip())

            # Capture final result or solution
            elif "result" in title or "solution" in title:
                result = text.strip()

        # Build a clear, user-friendly explanation
        response_parts = []
        if interpretation:
            response_parts.append(f"Interpretation:\n{interpretation}\n")

        if steps:
            response_parts.append("Step-by-step solution:")
            for i, step_text in enumerate(steps, 1):
                response_parts.append(f"Step {i}:\n{step_text}\n")

        if result:
            response_parts.append(f"Final Result:\n{result}")

        if response_parts:
            return "\n".join(response_parts)

        return "Sorry, I couldn't find a detailed answer to your question."

    except requests.exceptions.RequestException as e:
        return f"Error with the Wolfram Alpha request: {e}"
    except ET.ParseError:
        return "Error parsing the Wolfram Alpha response."
    except Exception as e:
        return f"Error: {str(e)}"

# ============= Casual Chat System =============
sid = SentimentIntensityAnalyzer()

def detect_emotion(text):
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.1:
        return "positive"
    elif compound <= -0.1:
        return "negative"
    else:
        return "neutral"

def casual_chat(user_name):
    print(f"Friend: Hey {user_name}! I'm excited to chat today. Mind if I ask you a few things?")

    chat_round = 0
    questions = [
        "How’s your day going so far?",
        "What’s something that made you smile today?",
        "Is there anything on your mind lately?",
        "What’s your ideal way to relax after a long day?",
        "Have you been working on anything fun or creative?",
        "What’s one thing you wish more people understood about you?"
    ]

    followups = {
        "positive": [
            "That’s really great to hear! 😄 Got anything else exciting going on?",
            "I love hearing that. What else has been going well lately?",
            "That energy is contagious — keep it up!"
        ],
        "negative": [
            "I’m sorry to hear that. Want to talk more about it?",
            "That sounds tough — I'm here if you need to vent.",
            "Sometimes just saying it out loud helps. I’m all ears."
        ],
        "neutral": [
            "Gotcha. Is there anything you're looking forward to?",
            "Hmm, sounds like a calm one. Anything new you're thinking about?",
            "Even ordinary days can be meaningful — anything you'd like to share more about?"
        ]
    }

    while True:
        if chat_round >= len(questions):
            print("Friend: I love these conversations. Is there anything you want to ask me now?")
        else:
            print(f"Friend: {questions[chat_round]}")

        user_input = input(f"{user_name}: ").strip().lower()

        if user_input in ["exit", "quit", "bye"]:
            print("Friend: It’s always a pleasure chatting with you. Let’s catch up again soon!")
            break

        # Basic keyword sentiment detection
        if any(word in user_input for word in ["good", "great", "awesome", "fantastic", "happy", "nice"]):
            mood = "positive"
        elif any(word in user_input for word in ["bad", "sad", "tired", "meh", "stress", "angry", "lonely"]):
            mood = "negative"
        else:
            mood = "neutral"

        print("Friend:", random.choice(followups[mood]))
        chat_round += 1
# ============= Mode Selector =============
def mode_selector(user_name, memory_logger):
    while True:
        mode_choice = input("\nEnter the number of the mode you want to activate (or 'exit' to quit): ").strip()

        if mode_choice.lower() == 'exit':
            print("Goodbye! You are now leaving the mode...")
            memory_logger.log_interaction("Exited mode selector", "")
            break

        memory_logger.log_interaction(f"Selected mode: {mode_choice}", "")

        if mode_choice == "1":
            handle_name_recognition(user_name, memory_logger)
        elif mode_choice == "2":
            handle_math_processing(user_name, memory_logger)
        elif mode_choice == "3":
            handle_book_recommendation(user_name, memory_logger)
        elif mode_choice == "4":
            start_budget_tracking(user_name)
        elif mode_choice == "5":
            handle_depression_screening(user_name, memory_logger)
        elif mode_choice == "6":
            handle_house_assistance(user_name, memory_logger)
        elif mode_choice == "7":
            handle_casual_chat(user_name, memory_logger)
        elif mode_choice == "8":
            memory_logger.view_log()
            memory_logger.log_interaction("Viewed memory log", "")
        elif mode_choice == "9":
            language_translation_mode(user_name, memory_logger)
        elif mode_choice == "10":
            handle_reminder_mode(user_name, memory_logger)
        elif mode_choice == "0":
            break 
        else:
            print("❌ Invalid mode choice. Please enter a valid number.")

# =============( Personal add on) Budget Tracker + budget  Advice System =============

user_budget_data = {}

def start_budget_tracking(user_name):
    if user_name not in user_budget_data:
        print(f"\nWelcome {user_name} Lets save some money, also remember dreams without goals are just dreams.")
        while True:
            try:
                goal = float(input("What is your savings goal? (Enter in dollars): $"))
                break
            except ValueError:
                print("Please enter a valid number.")

        user_budget_data[user_name] = {
            "goal": goal,
            "current": 0.0
        }

        print(f"Great! Your savings goal is ${goal:.2f}. Let's start saving!\n")

    while True:
        print("\nSelect an option:")
        print("1. Add saved amount")
        print("2. Check progress")
        print("3. Offer some budgeting tips!")
        print("4. I want to exit for now")

        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                amount = float(input("Enter how much you’ve saved to add to your progress: $"))
                user_budget_data[user_name]["current"] += amount

                # Check if goal reached
                current = user_budget_data[user_name]["current"]
                goal = user_budget_data[user_name]["goal"]

                if current >= goal:
                    print(f"\n🎉 Congratulations, {user_name}! You’ve reached your goal of ${goal:.2f}!")
                    print("The discipline you're building will changing your future. You are one step closer to financial freedom!.\n")
                else:
                    remaining = goal - current
                    print(f"You’ve saved ${current:.2f}. Only ${remaining:.2f} to go! Keep going, you're doing great!")

            except ValueError:
                print("Please enter a valid number.")

        elif choice == "2":
            goal = user_budget_data[user_name]["goal"]
            current = user_budget_data[user_name]["current"]
            progress = (current / goal) * 100 if goal != 0 else 0
            print(f"\nYour Goal: ${goal:.2f}")
            print(f"Current Savings: ${current:.2f}")
            print(f"Progress: {progress:.1f}%\n")

        elif choice == "3":
            question = input("What kind of budget help do you need? ")
            advice = generate_custom_response(question)
            print(f"💡 Advice: {advice}")

        elif choice == "4":
            print("Returning to the mode selector...\n")
            break

        else:
            print("Invalid option. Please select 1-4.")

# ============= Budget Advice Sub-System =============
def generate_custom_response(question):
    question = question.lower()

    if "save" in question or "goal" in question:
        return "Start with a SMART goal (Specific, Measurable, Achievable, Relevant, Time-bound). Break it into weekly targets."
    elif "track" in question or "habit" in question:
        return "Use visual progress (charts or meters) and reward small milestones. This reinforces good habits."
    elif "spending" in question:
        return "List your top 3 spending categories and challenge yourself to reduce just one by 10% this week."
    elif "debt" in question:
        return "Tackle the smallest debt first (snowball method) or the highest interest one (avalanche method)."
    else:
        return "Stuck? Try tracking every dollar for a week. You'll be surprised where your money goes!"

# ============= MAIN EXECUTION =============
def main():
    print("Hello, I am your personal AI companion! Fun fact: AI stands for artificial intelligence..\n")
    
    user_name = input("📝 Enter your name here: ").strip()
    print(f"\nNice to meet you, {user_name}! How can I help you today?")
    print("💡 Type 'modes' to see what I can do, or 'bye' to exit.\n")

    reminder_manager = ReminderManager(user_name)
    print("\n📬 Before we begin, here are your current reminders (if any):")
    reminder_manager.view_reminders()

    memory_logger = MemoryLogger(user_name)

    while True:
        user_input = input(f"{user_name}: ").strip().lower()

        if user_input in [
            "modes",
            "bring me to the modes",
            "go to modes",
            "take me to the modes",
            "take me to the mode selector",
            "i request the mode selector"
        ]:
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
            print("  0. EXIT THE MODE SELECTOR")

            memory_logger.log_interaction(user_input, "Viewed modes and entered mode selector")
            mode_selector(user_name, memory_logger)

        elif user_input == "bye":
            print(f"Chatbot: Goodbye {user_name}! Have a great day!")
            memory_logger.log_interaction(user_input, f"Goodbye {user_name}!")
            break

        else:
            response = "Sorry, please type 'modes' to open the mode selector or 'bye' to exit."
            print(f"Chatbot: {response}")
            memory_logger.log_interaction(user_input, response)



# ============= Book + Storytelling User Experience ==============
def get_book_from_openlibrary(query="science fiction"):
    url = f"https://openlibrary.org/search.json?q={query}&language=eng&has_fulltext=true"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data["docs"]:
            return f"Sorry, I couldn't find any books for '{query}'. Try another topic?"
        book = data["docs"][0]
        title = book.get("title", "Unknown Title")
        author = book.get("author_name", ["Unknown Author"])[0]
        ol_id = book.get("key", "")
        book_url = f"https://openlibrary.org{ol_id}"
        return f"📘 **{title}** by {author}\n🔗 Read or borrow here: {book_url}"
    except requests.exceptions.RequestException as e:
        return f"Error: Couldn't connect to Open Library API. Details: {str(e)}"

def get_book_and_story_video(topic, use_openlibrary=True, max_videos=5):
    # Use Open Library API if requested
    if use_openlibrary:
        book_info = get_book_from_openlibrary(topic)
    else:
        book_info = f"Here is a recommended book on {topic}."

    video_list = [
        ("Video 1 Chronicles of Narnia", "https://www.youtube.com/watch?v=smx1sn_BfaA"), 
        ("Video 2 The Hobbit", "https://www.youtube.com/watch?v=fFU3_vohIOs"),
        ("Video 3 Harry Potter","https://www.youtube.com/watch?v=FsByOCWSkvM"),
        ("Video 4 The Lord of the Rings", "https://www.youtube.com/watch?v=V75dMMIW2B4"),
        ("Video 5 Mrs Peregrine's Home for Peculiar Children","https://www.youtube.com/watch?v=2rhnt5rWgOM"),
    ]
    return book_info, video_list[:max_videos]

def book_and_storytelling_experience(youtube_api_key=None):
    print("\nWould you like to:")
    print("1. Discover some classic books guaranteed to bring you excitement.")
    print("2. Hear audiobooks from some classic books recommended by yours truly!")
    print("3. Do both (recommended read & watch experience!)")
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice not in ["1", "2", "3"]:
        print("Invalid option. Please choose 1, 2, or 3.")
        return

    topic = input("Enter a topic or genre (e.g., fantasy, science, adventure): ")

    # Always use Open Library
    book_info, video_list = get_book_and_story_video(topic, use_openlibrary=True, max_videos=5)

    if choice == "1":
        print(f"\n📚 Book Recommendation:\n{book_info}\n")
    elif choice == "2":
        run_video_loop(video_list)
    elif choice == "3":
        print(f"\n📚 Book Recommendation:\n{book_info}\n")
        run_video_loop(video_list)

def run_video_loop(video_list):
    print("\n🎥 Storytelling Videos:\n")
    current = 0
    while True:
        if current < len(video_list):
            title, link = video_list[current]
            print(f"🎥 Video {current + 1}: {title}\nWatch here: {link}\n")
        else:
            print("No more videos available.")
            break

        next_step = input("Type 'next' to see another video, or 'exit' to quit: ").strip().lower()
        if next_step == "next":
            current += 1
        elif next_step == "exit":
            print("👋 I hope you come back to explore more interesting stories!")
            break
        else:
            print("Please type 'next' or 'exit'.")
    
    def run_flask():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    if '--cli' in sys.argv:
        main()  


