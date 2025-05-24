
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

#NOTE:
#- Sensitive keys are loaded from environment variables.
#- Ensure .env file is in .gitignore to keep secrets safe.





import random
import requests
from requests.models import encode_multipart_formdata
import os
from xml.etree import ElementTree as ET
from flask import Flask, request, jsonify
import threading
import wolframalpha
import openai
from dotenv import load_dotenv


def ensure_safe_gitignore():
    gitignore_path = '.gitignore'
    safe_ignore_content = ("")


    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(safe_ignore_content.strip())
        print("✅ Created a safe .gitignore file.")
    else:
        print(".gitignore file already exists.")

# Call the function early in your main script or setup process
ensure_safe_gitignore()



load_dotenv()
 

youtube_api_key = os.getenv('YT_IYKYK')


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
        print(f"Chatbot: Hello, {user_name}, it's great to see you again, How could I make today feel more special?")
    else:
        print(f"Chatbot: Nice to meet you, {known_names}, you look wonderful today!")



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
            "output": "XML"
        }
        response = requests.get(WOLFRAM_API_URL, params=params)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.text)
        for pod in root.findall(".//pod"):
            title = pod.get("title", "").lower()
            if "result" in title or "solution" in title:
                plaintext = pod.find(".//plaintext")
                if plaintext is not None and plaintext.text:
                    return f"Result: {plaintext.text}"

        return "Sorry, I couldn't find an answer to your question."

    except requests.exceptions.RequestException as e:
        return f"Error with the Wolfram Alpha request: {e}"
    except ET.ParseError:
        return "Error parsing the Wolfram Alpha response."
    except Exception as e:
        return f"Error: {str(e)}"
        
# Send a GET request directly to the Wolfram Alpha API

# ============= Casual Chat System =============
def casual_chat(user_name):
    print(f"Hey {user_name}! How’s your day going so far?")

    state = "start"

    while True:
        user_input = input(f"{user_name}: ").strip().lower()

        if user_input in ["exit", "quit", "bye"]:
            print("It was so lovely chatting with you, can wait to talk to you again! ")
            break

        if state == "start":
            if any(word in user_input for word in ["good", "great", "amazing", "awesome", "fantastic"]):
                responses = [
                    "Friend: That's wonderful to hear! What’s been the highlight of your day?",
                    "Friend: I love that energy! Anything specific that made it great?",
                    "Friend: Good days are worth celebrating! Did something exciting happen?"
                ]
                print(random.choice(responses))
                state = "positive"
            elif any(word in user_input for word in ["bad", "tired", "sad", "stress", "angry"]):
                responses = [
                    "Friend: I'm really sorry to hear that. Want to talk about it?",
                    "Friend: That sounds rough. I'm here if you want to vent or chat about something lighter.",
                    "Friend: Oof, tough day huh? Let me know how I make you feel better!"
                ]
                print(random.choice(responses))
                state = "negative"
            else:
                responses = [
                    "Friend: Hmm, sounds like an interesting day! Tell me more.",
                    "Friend: Gotcha. Want to dive into anything specific?",
                    "Friend: I'm all ears — what happened today?"
                ]
                print(random.choice(responses))
                state = "neutral"

        elif state == "positive":
            responses = [
                "Friend: You really are an interesting character — I like that about you!",
                "Friend: I’m glad to see you in such a good mood. It’s contagious!",
                "Friend: Keep that vibe going, you're doing great!"
            ]
            print(random.choice(responses))
            state = "continue_positive"

        elif state == "negative":
            responses = [
                "Friend: I’m here for you. Sometimes just talking helps — feel free to vent.",
                "Friend: That sounds heavy. I'm not a therapist, but I can definitely listen.",
                "Friend: Whatever you're feeling, you're not alone in it. Want to chat more?"
            ]
            print(random.choice(responses))
            state = "continue_negative"

        elif state == "neutral":
            responses = [
                "Friend: I love hearing about your day! What else is on your mind?",
                "Friend: It sounds like today had its ups and downs — want to dive deeper?",
                "Friend: Thanks for sharing that. Anything else on your plate?"
            ]
            print(random.choice(responses))
            state = "continue_neutral"

        elif state in ["continue_positive", "continue_negative", "continue_neutral"]:
            if "you" in user_input:
                responses = [
                    "Friend: Aww, thanks for asking! I’m just happy to be here with you.",
                    "Friend: Me? I'm doing just fine. I enjoy hearing about your life!",
                    "Friend: I’ve been thinking a lot lately — about how cool these chats are."
                ]
            else:
                responses = [
                    "Friend: That's really interesting! Tell me more.",
                    "Friend: You're full of surprises — what's next?",
                    "Friend: That’s something worth exploring. Want to keep going?"
                ]
            print(random.choice(responses))




# ============= Mode Selector =============
def mode_selector(user_name):
    print("\nSelect a mode:")
    print("1. Main AI Companion Loop")
    print("2. Name Recognition System")
    print("3. Math Processing System")
    print("4. Book Recommendation + storytelling system")
    print("5. Budget tracker + Budget Advice system")
    print("6. Determine your emotional state")
    print("7. House tidying")
    print("8. Casual Chat")

    while True:
        mode_choice = input("\nEnter the number of the mode you want to activate (or 'exit' to quit): ")

        if mode_choice.lower() == 'exit':
            print("Goodbye! Exiting the program...")
            break  # Exit the mode selector loop if user wants to quit.

        # Loop through each mode, keeping the user in the selected mode until they exit
        if mode_choice == "1":
            print("\n=== Main AI Companion Loop ===")
            main()  # Start the main AI loop and let them interact
        elif mode_choice == "2":
            print("\n=== Name Recognition System ===")
            name = input("Enter a name to check: ")
            check_name(name)
        elif mode_choice == "3":
            print("\n=== Math Processing System ===")
            question = input("Enter a math question: ")
            result = handle_math_question(question)
            print(f"Result: {result}")
        elif mode_choice == "4":
            print("\n=== Book Recommendation and Storytelling Experience ===")
            if youtube_api_key:
                book_and_storytelling_experience(youtube_api_key)
            else:
                print("❌ YouTube API key not found in environment variable 'YT_IYKYK'")
        elif mode_choice == "5":
            print("\n=== Budget Tracking + Advice System ===")
            start_budget_tracking(user_name)
        
        elif mode_choice == "6":
            print("\n=== Depression Screening ===")
            total_score = 0
            print("\nPlease answer the following questions with a number from 0-3:")
            print("0: None of the time")
            print("1: Sometimes")
            print("2: Quite a bit")
            print("3: Most or all of the time")

            for i, question in enumerate(depression_questions, 1):
                while True:
                    try:
                        score = int(input(f"\nQ{i}. {question}\nYour answer (0-3): "))
                        if 0 <= score <= 3:
                            total_score += score
                            break
                        else:
                            print("Please enter a number between 0 and 3.")
                    except ValueError:
                        print("Please enter a valid number.")

            severity = get_depression_severity(total_score)
            suggestion = get_suggestion(severity)
            print(f"\nBased on your responses:")
            print(f"Severity Level: {severity}")
            print(f"Suggestion: {suggestion}")
        elif mode_choice == "7":
            print("\n=== House Assistance ===")
            print("Available topics: cleaning, energy, security, organization, automation")
            topic = input("Enter a topic for house tidying advice: ")
            advice = house_tidying(topic)
            print(f"Advice: {advice}")

            # Loop here to keep providing house tidying tips until the user exits
            while True:
                exit_choice = input("\nDo you want to continue with more house tidying tips or exit? (Enter 'continue' to get more tips or 'exit' to go back to the modes): ").lower()
                if exit_choice == 'continue':
                    topic = input("Enter a new topic for house tidying advice: ")
                    advice = house_tidying(topic)
                    print(f"Advice: {advice}")
                elif exit_choice == 'exit':
                    print("Returning to mode selector...")
                    break  # Break the inner loop to return to mode selection
                else: print("I cannot do that right now. Please type 'continue' or 'exit'.")
        elif mode_choice == "8":
            print("\n=== Casual Chat ===")
            casual_chat(user_name)
        else:
            print("Invalid choice. Please select a valid mode number.")


# ============= Main AI Companion Loop =============
def main():
    print("Hello, I am your personal AI companion! Fun fact: AI stands for artificial intelligence..")
    user_name = input("Please type your name then type 'modes' to bring up the mode selector.!").strip()
    print(f"Nice to meet you, {user_name}! How can I help you today?") #Fix which introduction you want

    while True:
        user_input = input(f"{user_name}: ").lower()

        if user_input in ["modes", "bring me to the modes", "go to modes", "take me to the modes", "take me to the mode selector", "I request the mode selector"]:
            mode_selector(user_name)
        elif user_input == "bye":
            print(f"Chatbot: Goodbye {user_name}! Have a great day!")
            break






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
if __name__ == '__main__':
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(
    target=app.run,
    kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': True, 'use_reloader': False}
)
    flask_thread.start()




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

# Run Flask and main companion loop simultaneously (with threading)
if __name__ == '__main__':
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False, 'use_reloader': False})
    flask_thread.start()

    main()