import tkinter as tk
from tkinter import scrolledtext, simpledialog
from voice_gui_assistant import VisualCompanionApp
import threading
import os
import requests
from random import choice
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import pygame
import hashlib

from voice_input import get_input  # Voice input fallback
from chat_data import positive_questions, negative_questions, neutral_questions, followups, transition_comments

# ========== Initialization ==========
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("EL_API_KEY")
DEFAULT_VOICE_ID = "VR6AewLTigWG4xSOukaG"  # Male voice ID

pygame.mixer.init()
sid = SentimentIntensityAnalyzer()

# ========== Helpers ==========
def get_cache_path(text):
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    hashed_name = hashlib.md5(text.encode()).hexdigest()
    return os.path.join(cache_dir, f"{hashed_name}.mp3")

def speak_with_elevenlabs(text, voice_id):
    audio_path = get_cache_path(text)
    if os.path.exists(audio_path):
        return audio_path

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

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return audio_path
    except Exception as e:
        print("❌ ElevenLabs error:", e)
        return None

def detect_emotion(text):
    compound = sid.polarity_scores(text)['compound']
    if compound >= 0.1:
        return "positive"
    elif compound <= -0.1:
        return "negative"
    return "neutral"

# ========== GUI App Class ==========
class VisualAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ AI Voice Assistant")
        self.voice_id = DEFAULT_VOICE_ID

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

        self.voice_button = tk.Button(root, text="🎤 Speak", command=self.handle_voice_input, font=("Helvetica", 12))
        self.voice_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

        self.user_name = simpledialog.askstring("Welcome!", "👋 What's your name?", parent=root) or "Friend"

        self.past_questions = set()
        self.current_question_index = 0
        self.turns_since_transition = 0

        greeting = f"Hey {self.user_name}! Let's chat. {self.get_next_question()}"
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
            user_text = get_input("Speak your input:")
            if not user_text:
                return
            self.entry.insert(0, user_text)

        self.display_message(self.user_name, user_text)
        self.entry.delete(0, tk.END)

        if user_text.lower() in ["bye", "exit", "quit"]:
            goodbye = "It’s always a pleasure chatting with you. Let’s catch up again soon!"
            self.display_response(goodbye)
            self.play_response(goodbye)
            self.root.after(2500, self.root.quit)
            return

        response = self.get_conversation_response(user_text)
        self.display_response(response)
        self.play_response(response)

    def handle_voice_input(self):
        def mic_thread():
            self.display_response("Listening...")
            try:
                voice_text = get_input("Speak something:")
                if voice_text:
                    self.display_message(self.user_name, voice_text)
                    response = self.get_conversation_response(voice_text)
                    self.display_response(response)
                    self.play_response(response)
            except Exception as e:
                self.display_response("🎤 Mic error.")
                print("Voice input error:", e)

        threading.Thread(target=mic_thread, daemon=True).start()

    def get_conversation_response(self, user_text):
        mood = detect_emotion(user_text)

        if self.turns_since_transition >= 3:
            transition = choice(transition_comments)
            self.turns_since_transition = 0
            return transition

        followup_list = followups[mood]
        response = choice(followup_list)

        self.current_question_index += 1
        if self.current_question_index >= len(positive_questions):
            self.current_question_index = 0

        next_question = self.get_next_question()
        response = f"{response} {next_question}"

        self.turns_since_transition += 1
        return response

    def get_next_question(self):
        question_pool = positive_questions

        available = [q for q in question_pool if q not in self.past_questions]
        if not available:
            self.past_questions.clear()
            available = question_pool[:]

        chosen = choice(available)
        self.past_questions.add(chosen)
        return chosen

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
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print("🎧 Playback error:", e)

# ========== External Entry Point ==========
def run_voice_assistant_gui():
    root = tk.Tk()
    app = VisualCompanionApp(root)
    root.mainloop()
