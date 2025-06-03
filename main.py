
#"""
# AI Companion - main.py
#Version: V1

#Features:
#- Mode selector with multiple functionalities
#- Math processing via WolframAlpha API
#- House tidying advice
#- Budget tracking and advice
#- Book recommendation and storytelling
#- Casual chat system
#- Name recognition system
#- Flask server for API extensions
#- Language translation system
#- Task reminder system


#NOTE:
#- Sensitive keys are loaded from environment variables.
#- Ensure .env file is in .gitignore to keep secrets safe.


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
    topic = input("Enter a topic or genre (e.g., fantasy, science, adventure, romance, comedy, action, psychological horror): ").strip()
    memory_logger.log_interaction(topic, "")
    if youtube_api_key:
        book_and_storytelling_experience(youtube_api_key)
    else:
        print("❌ YouTube API key not found.")
        memory_logger.log_interaction(topic, "YouTube API key missing")


def handle_depression_screening(user_name, memory_logger):
    print("\n=== PHQ-9 Depression Screening ===")
    
    questions = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling or staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself — or that you are a failure or have let yourself or your family down?",
        "Trouble concentrating on things, such as reading the newspaper or watching television?",
        "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving a lot more than usual?",
        "Thoughts that you would be better off dead or of hurting yourself in some way?"
    ]

    options_text = (
        "\nPlease answer each question based on the past 2 weeks:\n"
        "0 = Not at all\n"
        "1 = Several days\n"
        "2 = More than half the days\n"
        "3 = Nearly every day"
    )
    print(options_text)

    total_score = 0
    responses = []

    for idx, question in enumerate(questions, 1):
        while True:
            try:
                answer = input(f"\n{idx}. Over the last 2 weeks, how often have you experienced the following:\n{question}\nYour answer (0-3): ").strip()
                if answer in ('0', '1', '2', '3'):
                    answer_int = int(answer)
                    responses.append(answer_int)
                    total_score += answer_int
                    memory_logger.log_interaction(question, answer_int)
                    break
                else:
                    print("Invalid input. Please enter a number from 0 to 3.")
            except Exception as e:
                print(f"An error occurred: {e}")

    print("\n=== Screening Results ===")
    print(f"Total Score: {total_score} out of 27")

    # PHQ-9 score interpretation
    if total_score <= 4:
        severity = "Minimal depression"
    elif 5 <= total_score <= 9:
        severity = "Mild depression"
    elif 10 <= total_score <= 14:
        severity = "Moderate depression"
    elif 15 <= total_score <= 19:
        severity = "Moderately severe depression"
    else:
        severity = "Severe depression"

    print(f"Depression Severity: {severity}")

    # Safety check for question 9 (suicidal thoughts)
    if responses[8] > 0:
        print("\n!! Your response indicates thoughts of self-harm or suicide.")
        print("Please consider talking to a mental health professional immediately or calling a helpline.")

    print("\nThis screening is not a diagnosis. Please consult a professional for a full evaluation.")

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
        "cleaning": [
            "Start with a 10-minute tidy-up: Set a timer and focus on one room.",
            "Break cleaning into zones: kitchen, bathroom, living areas, bedroom.",
            "Keep a caddy with basic supplies (spray, cloths, gloves) in each bathroom.",
            "Do one laundry load a day to avoid overwhelming piles.",
            "Always clean as you go — especially in the kitchen to stay ahead of messes."
        ],
        "energy": [
            "Unplug unused electronics — they still draw power in standby mode.",
            "Switch to LED bulbs to reduce energy consumption.",
            "Set your thermostat 1–2 degrees lower in winter and higher in summer to save energy.",
            "Use natural light during the day whenever possible.",
            "Install a smart power strip to manage multiple devices efficiently."
        ],
        "security": [
            "Install motion-sensor lights at entrances and around the backyard.",
            "Use a smart doorbell to monitor activity at your front door.",
            "Keep bushes and trees trimmed to remove hiding spots near windows.",
            "Lock windows and sliding doors at night and when away.",
            "Create a daily routine to check locks and lights before bed."
        ],
        "organization": [
            "Declutter one drawer or shelf a day — small steps build momentum.",
            "Use clear bins so you can see what’s stored inside without opening everything.",
            "Add hooks by the front door for keys, bags, and coats.",
            "Label everything — it helps everyone in the household stay organized.",
            "Use the ‘one in, one out’ rule: for every new item, donate or toss an old one."
        ],
        "automation": [
            "Set routines with your smart assistant (e.g., ‘Good Morning’ to start lights and coffee).",
            "Use smart plugs to schedule appliances like humidifiers or lamps.",
            "Automate vacuuming with a robot vacuum — it saves time every day.",
            "Enable geofencing so lights and thermostats adjust when you leave/arrive.",
            "Use sensors to turn off lights in empty rooms automatically."
        ]
    }

    topic_key = topic.lower()
    if topic_key in tips:
        print(f"\n=== {topic.capitalize()} Tips ===")
        for i, tip in enumerate(tips[topic_key], 1):
            print(f"{i}. {tip}")
    else:
        print("\nI happen to be very knowledgble in these specific styles so please ask away! ")
        print("- Cleaning\n- Energy\n- Security\n- Organization\n- Automation")




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
    question = question.lower().strip()

    if any(word in question for word in ["invest", "investment", "stocks", "portfolio"]):
        return (
            "Smart move thinking about investing. Before diving in, ask yourself: "
            "Do I have an emergency fund set aside? Start with index funds or ETFs — they’re low-risk and great for beginners. "
            "Remember, investing is a long-term game, not a get-rich-quick scheme."
        )

    elif any(word in question for word in ["save", "goal", "savings", "set aside"]):
        return (
            "Great! Start with a SMART goal — Specific, Measurable, Achievable, Relevant, Time-bound. "
            "For example, instead of 'I want to save money', try 'I’ll save $50/week for 6 months to build a $1200 emergency fund.' "
            "Clarity fuels discipline."
        )

    elif any(word in question for word in ["track", "habit", "monitor", "routine"]):
        return (
            "Tracking is key. Start small: list your expenses daily for just one week. "
            "Patterns will emerge. Pair that with a visual tracker — like a habit app or spreadsheet. "
            "The goal? Make progress visible and addictive."
        )

    elif any(word in question for word in ["spending", "expenses", "bills", "cost"]):
        return (
            "Challenge yourself: write down your top 3 spending categories. "
            "Then cut back just 10% in one of them this week. No shame — just insight. "
            "Spend with intention, not impulse."
        )

    elif any(word in question for word in ["debt", "owe", "loan", "credit card"]):
        return (
            "Debt can feel heavy, but there’s a path out. Use the snowball method (smallest balance first) for momentum, "
            "or the avalanche method (highest interest first) to save more long term. "
            "Either way — pay *more than the minimum*. Every dollar over counts more than you think."
        )

    elif any(word in question for word in ["budget", "plan", "allocate", "money management"]):
        return (
            "Think of your budget like a map — it tells your money where to go instead of wondering where it went. "
            "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings/debt. "
            "Tweak it to fit your life — the point is to be *intentional* with every dollar."
        )

    elif any(word in question for word in ["emergency", "rainy day", "unexpected", "backup"]):
        return (
            "Emergencies happen. That’s why even setting aside $500 is powerful. "
            "It gives you breathing room — and peace of mind. Start small: automate $10–$20 weekly into a separate account. "
            "Your future self will thank you."
        )

    else:
        return (
            "Good question. When in doubt, do this: for the next 7 days, write down *every* dollar you spend. "
            "Don’t judge it, just log it. Awareness is the first step to control. "
            "You don’t need more money, you need a stricter mindset with how your money is being spent. 💪"
        )

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
# --- Book Lookup ---
def get_book_from_openlibrary(query="science fiction"):
    """
    Fetches a book from Open Library based on the given query.
    """
    base_url = "https://openlibrary.org"
    search_url = f"{base_url}/search.json?q={query}&language=eng&has_fulltext=true"

    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data["docs"]:
            return f"📚 Sorry, I couldn't find any books for '{query}'. Try another topic?"

        book = data["docs"][0]
        title = book.get("title", "Unknown Title")
        author = book.get("author_name", ["Unknown Author"])[0]
        ol_id = book.get("key", "")
        book_url = f"{base_url}{ol_id}"

        return f"📘 **{title}** by {author}\n🔗 Read or borrow here: {book_url}"

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error: Couldn't connect to Open Library. Details: {str(e)}"


def get_video_lists():
    """
    Returns the dictionary of video lists by genre.
    """
    return {
        "fantasy": [
            ("Chronicles of Narnia", "https://www.youtube.com/watch?v=smx1sn_BfaA"),
            ("The Hobbit", "https://www.youtube.com/watch?v=fFU3_vohIOs"),
            ("Harry Potter", "https://www.youtube.com/watch?v=FsByOCWSkvM"),
            ("The Lord of the Rings", "https://www.youtube.com/watch?v=V75dMMIW2B4"),
            ("Miss Peregrine's Home for Peculiar Children", "https://www.youtube.com/watch?v=2rhnt5rWgOM"),
            ("Forsaken Prince: Kilenya Chronicles Book One", "https://www.youtube.com/watch?v=gYohVoi_m_A&list=PL6kepgWUZXmp-el3a0z0IoqDhUDn4kyUg"),
            ("Ember Gods: Kilenya Chronicles Book Two", "https://www.youtube.com/watch?v=OrQugg3zYAI"),
            ("The Eyes of the Dragon by Stephen King", "https://www.youtube.com/watch?v=ycxRUnmG5ZE"),
        ],
        "science": [
            ("A Voyage to Arcturus by David Lindsay", "https://www.youtube.com/watch?v=90hLehiXM8g"),
            ("Supermind by Laurence M. Janifer & Randall Garrett", "https://www.youtube.com/watch?v=20of1yvGh5Y"),
            ("The Last Question", "https://www.youtube.com/watch?v=h4M3nL_Vb9w"),
            ("Pacific Rim by Travis Beacham", "https://www.youtube.com/watch?v=0IxQ4KLmcA0"),
            ("Hyperion by Dan Simmons", "https://www.youtube.com/watch?v=0uEBG98-bcY"),
            ("Worlds Within by Rog Phillips", "https://www.youtube.com/watch?v=NZKWTDEzRL4"),
            ("The Alchemy of Happiness by Al-Ghazali", "https://www.youtube.com/watch?v=0Ox_XcrBO0c"),
        ],
        "adventure": [
            ("The maze runner by Robert Daschner", "https://www.youtube.com/watch?v=sKJ1ktsVq-k&list=PLq5SGWgwX4FZt88QFxL_IDtvJd46Mtwgy"),
            ("The Dark Tower: The Gunslinger by Stephen King", "https://www.youtube.com/watch?v=ybvVLVaGiUM"),
            ("The Dark Tower: The Drawing of the Three by Stephen King", "https://www.youtube.com/watch?v=CWt5DFbGSyI"),
            ("The Dark Tower: The Waste Lands by Stephen King", "https://www.youtube.com/watch?v=vl8UK2wwBg0"),
            ("The Dark Tower: Wizard and Glass by Stephen King", "https://www.youtube.com/watch?v=Dy6kqY45csc"),
            ("The Dark Tower: The Dark Tower by Stephen King", "https://www.youtube.com/watch?v=cIkq1dKqfL0"),
        ],
        "romance": [
            ("Falling for the Movie Star by Jean Oram", "https://www.youtube.com/watch?v=rvUqJWb6FJs"),
            ("Gone With The Wind by Margaret Mitchell", "https://www.youtube.com/watch?v=pI__6gL21Co"),
            ("To all the boys I have loved before by Jenny Han ", "https://www.youtube.com/watch?v=Ac_fbiCvWDk, or https://www.youtube.com/watch?v=qdEcvQ5P0g4"),
            ("Pride and Prejudice by Jane Austen", "https://www.youtube.com/watch?v=eVHu5-n69qQ"),
            ("Outlander by Diana Gabaldon", "https://www.youtube.com/watch?v=cY-L5pqCCrU"),
            ("A Walk to Remember by Nicholas Sparks", "https://www.youtube.com/watch?v=ekX1c-y6xJQ"),
            ("The Fault in Our Stars by John Green", "https://www.youtube.com/watch?v=ht94ebGbScs"),
            ("The Time Traveler’s Wife by Audrey Niffenegger", "https://www.youtube.com/watch?v=uZNRMHAWl9w"),
        ],
        "comedy": [
            ("under the dome by Stephen King", "https://www.youtube.com/watch?v=UvYyzTQVy4w"),
            ("Oliver twist by Charles Dickens", "https://www.youtube.com/watch?v=cUVyaRJhKwc"),
            ("UNCLE toms Cabin by Harriet Beecher Stowe", "https://www.youtube.com/watch?v=hJUr-vS29dU"),
            ("Good Omens by Neil Gaiman & Terry Pratchett", "https://www.youtube.com/watch?v=h2GPXnANyGk"),
            ("The Hitchhiker's Guide to the Galaxy by Douglas Adams", "https://www.youtube.com/watch?v=33WOUNcAas4"),
            ("Bossypants by Tina Fey", "https://www.youtube.com/watch?v=Gzs5-C9Hu14"),
            ("Yes Please by Amy Poehler", "https://www.youtube.com/watch?v=IqVcHwKhr1Y"),
        ],
    }


def get_book_and_story_video(topic, max_videos=5):
    """
    Returns a book recommendation and up to `max_videos` related videos for the genre.
    """
    book_info = get_book_from_openlibrary(topic.lower())
    video_lists = get_video_lists()
    video_list = [item for item in video_lists.get(topic.lower(), []) if item[0] and item[1]]
    return book_info, video_list[:max_videos]


def run_video_loop(video_list):
    """
    Iterates through the video list, letting the user move through or exit.
    """
    print("\n🎥 Storytelling Videos:\n")
    current = 0
    while current < len(video_list):
        title, link = video_list[current]
        print(f"🎬 Video {current + 1} of {len(video_list)}: {title}\n🔗 Watch here: {link}\n")
        next_step = input("Type 'next' to continue or 'exit' to stop: ").strip().lower()
        if next_step != "next":
            print("👋 Exiting video loop.")
            break
        current += 1
    if current >= len(video_list):
        print("🎉 Congratulations you've reached the end of the video list!")


def book_and_storytelling_experience():
    """
    Interactive CLI for choosing a book, video, or both based on a genre.
    """
    print("\nChoose your literary journey:")
    print("1. Discover a great book 📖")
    print("2. Watch audiobooks or storytelling videos 🎧")
    print("3. Get both reading & video experiences 💡")

    choice = input("Enter 1, 2, or 3: ").strip()
    if choice not in {"1", "2", "3"}:
        print("❌ Invalid option. Please choose 1, 2, or 3.")
        return

    topic = input("\nEnter a topic or genre (e.g., fantasy, science, adventure, romance, comedy): ").strip().lower()
    book_info, video_list = get_book_and_story_video(topic)

    if choice == "1":
        print(f"\n📚 Book Recommendation:\n{book_info}")
    elif choice == "2":
        if video_list:
            run_video_loop(video_list)
        else:
            print(f"😕 Sorry, no videos found for genre '{topic}'.")
    elif choice == "3":
        print(f"\n📚 Book Recommendation:\n{book_info}")
        if video_list:
            run_video_loop(video_list)
        else:
            print(f"😕 Sorry, no videos found for genre '{topic}'.")


if __name__ == '__main__':
    if '--cli' in sys.argv:
        main()

