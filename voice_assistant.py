import requests
import os
from dotenv import load_dotenv
from random import choice
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("EL_API_KEY")
if not ELEVENLABS_API_KEY:
    print("⚠️ ElevenLabs API key not found in environment variables.")

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

def speak_with_elevenlabs(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        file_path = "output.mp3"
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio saved as {file_path}.")
    else:
        print("❌ Error from ElevenLabs:", response.status_code, response.text)

def casual_chat(use_voice=True):
    # User name prompt
    user_name = input("👋 Hi there! Type your name to get started: ").strip().title()
    if not user_name:
        user_name = "Friend"

    # 🎤 Voice selection
    voice_choice = input("🎤 Would you like a Male or Female voice? (M/F): ").strip().lower()


# ===== URL FOR VOICE ID https://elevenlabs.io/app/speech-synthesis/speech-to-speech
    # 🧠 Replace the voice IDs below with your own
    MALE_VOICE_ID = ""       # MALE VOICE ID
    FEMALE_VOICE_ID = "paste-your-female-voice-id-here"   # FEMALE VOICE ID

    # Use selected voice
    if voice_choice == "m":
        voice_id = MALE_VOICE_ID
    else:
        voice_id = FEMALE_VOICE_ID

    # Greeting
    greeting = f"Hey {user_name}! I'm excited to chat today. Mind if I ask you a few things?"
    print(f"Friend: {greeting}")
    if use_voice:
        speak_with_elevenlabs(greeting, voice_id)

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

    followup_phase = False
    followup_intro_given = False

    while True:
        if not followup_phase:
            if chat_round < len(questions):
                prompt = questions[chat_round]
            else:
                followup_phase = True
                prompt = "I love these conversations. Is there anything you want to ask me now?"
                followup_intro_given = True
        elif not followup_intro_given:
            prompt = "I love these conversations. Is there anything you want to ask me now?"
            followup_intro_given = True
        else:
            prompt = None

        if prompt:
            print(f"Friend: {prompt}")
            if use_voice:
                speak_with_elevenlabs(prompt, voice_id)

        user_input = input(f"{user_name}: ").strip().lower()
        if user_input in ["exit", "quit", "bye"]:
            goodbye = "It’s always a pleasure chatting with you. Let’s catch up again soon!"
            print(f"Friend: {goodbye}")
            if use_voice:
                speak_with_elevenlabs(goodbye, voice_id)
            break

        mood = detect_emotion(user_input)
        followup = choice(followups[mood])
        print(f"Friend: {followup}")
        if use_voice:
            speak_with_elevenlabs(followup, voice_id)

        if not followup_phase:
            chat_round += 1

if __name__ == "__main__":
    casual_chat(use_voice=True)