
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading
import os
import requests
from random import choice
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import pygame

# --- Setup ---
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("EL_API_KEY")
if not ELEVENLABS_API_KEY:
    print("⚠️ ElevenLabs API key not found in environment variables.")

pygame.mixer.init()
sid = SentimentIntensityAnalyzer()

# --- ElevenLabs Voice ---
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
        return file_path
    else:
        print("❌ ElevenLabs error:", response.status_code, response.text)
        return None

# --- Emotion/Intent ---
def detect_emotion(text):
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.1:
        return "positive"
    elif compound <= -0.1:
        return "negative"
    else:
        return "neutral"

def get_intent_based_response(user_input):
    text = user_input.lower()
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hey there! 👋 It’s always nice to hear a friendly hello."
    elif "how are you" in text:
        return "I'm doing great, thanks for asking! How about you?"
    elif "thank you" in text or "thanks" in text:
        return "You’re very welcome. I’m always here when you need me."
    elif any(word in text for word in ["bye", "goodbye", "see you"]):
        return "It’s always a pleasure chatting with you. Let’s catch up again soon!"
    return None

# --- GUI ---
class VisualAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ AI Voice Assistant")
        self.MALE_VOICE_ID = "VR6AewLTigWG4xSOukaG"
        self.FEMALE_VOICE_ID = "9BWtsMINqrJLrRacOk9x"
        self.voice_id = self.MALE_VOICE_ID

        self.chat_area = scrolledtext.ScrolledText(
            root, state=tk.DISABLED, wrap=tk.WORD,
            width=60, height=20, font=("Helvetica", 12)
        )
        self.chat_area.pack(padx=10, pady=10)

        self.entry = tk.Entry(root, width=50, font=("Helvetica", 12))
        self.entry.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))
        self.entry.bind("<Return>", self.handle_input)

        self.send_button = tk.Button(root, text="Send", command=self.handle_input, font=("Helvetica", 12))
        self.send_button.pack(side=tk.LEFT, padx=10, pady=(0, 10))

        self.user_name = simpledialog.askstring("Welcome!", "👋 What's your name?", parent=root)
        if not self.user_name:
            self.user_name = "Friend"

        greeting = f"Hey {self.user_name}! I'm excited to chat today. Mind if I ask you a few things?"
        self.display_response(greeting)
        self.play_response(greeting)

    def display_message(self, sender, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {text}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

  def handle_input(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.display_message(self.user_name, user_text)
        self.play_response(user_text)  # <-- 👈 This makes it speak what the user types
        self.entry.delete(0, tk.END)

        if user_text.lower() in ["bye", "exit", "quit"]:
            goodbye = "It’s always a pleasure chatting with you. Let’s catch up again soon!"
            self.display_response(goodbye)
            self.play_response(goodbye)
            self.root.after(2500, self.root.quit)
            return

        intent_response = get_intent_based_response(user_text)
        if intent_response:
            self.display_response(intent_response)
            self.play_response(intent_response)
        else:
            mood = detect_emotion(user_text)
            responses = {
                "positive": [
                    "That’s really great to hear! 😄 Got anything else exciting going on?",
                    "That energy is contagious — keep it up!"
                ],
                "negative": [
                    "I’m really sorry to hear that. Want to talk more about it?",
                    "That sounds tough — I'm here for you."
                ],
                "neutral": [
                    "Hmm, sounds like a chill day. What's been on your mind?",
                    "Even slow days can be meaningful — want to share more?"
                ]
            }
            reply = choice(responses[mood])
            self.display_response(reply)
            self.play_response(reply)

    def display_response(self, text):
        self.display_message("Friend", text)

    def play_response(self, text):
        threading.Thread(target=self._play_audio, args=(text,), daemon=True).start()

    def _play_audio(self, text):
        audio_path = speak_with_elevenlabs(text, self.voice_id)
        if audio_path:
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                # Wait for the audio to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print("🎧 Playback error:", e)

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = VisualCompanionApp(root)
    root.mainloop()


