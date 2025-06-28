import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading
import re
import random
import webbrowser
import os
import hashlib
import requests
import pygame
import speech_recognition as sr
from dotenv import load_dotenv

from chat_data import positive_questions, negative_questions, neutral_questions, followups, transition_comments
from belief_system import BeliefModel

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "VR6AewLTigWG4xSOukaG"
GOOGLE_API_KEY = os.getenv("CSE_IFYKYK")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

positive_words = {"happy", "great", "good", "love", "excited", "awesome", "joy", "grateful", "fun"}
negative_words = {"sad", "tired", "depressed", "upset", "angry", "bad", "lonely", "anxious"}

def clean_text(text):
    # Remove non-ASCII characters to prevent API errors
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def detect_emotion(text):
    lowered = text.lower()
    if any(word in lowered for word in positive_words):
        return "positive"
    elif any(word in lowered for word in negative_words):
        return "negative"
    return "neutral"

def search_google_cse(query):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return "Google Custom Search credentials are missing."
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params={
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 1
        })
        response.raise_for_status()
        items = response.json().get("items")
        if items:
            snippet = items[0]["snippet"]
            link = items[0]["link"]
            return f"{snippet}\n🔗 {link}"
        return "I couldn't find an answer to that."
    except Exception as e:
        print("Google CSE API error:", e)
        return "Sorry, something went wrong while searching."


def get_cache_path(text):
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    hashed_name = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(cache_dir, f"{hashed_name}.mp3")


def speak_with_elevenlabs(text, voice_id):
    audio_path = get_cache_path(text)
    text = clean_text(text[:2400])
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


class VisualCompanionApp:
    def __init__(self, root, user_name=None):
        self.root = root
        self.root.title("🧠 AI Companion")

        self.user_name = user_name or simpledialog.askstring("Welcome!", "What's your name?", parent=root) or "Friend"
        self.belief_model = BeliefModel(self.user_name)

        self.past_questions = set()
        self.user_memory = []
        self.last_question = None

        # Initialize pygame mixer once
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Warning: pygame mixer init failed: {e}")

        # --- Chat Display Area ---
        self.chat_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, width=60, height=20,
                                                   font=("Helvetica", 12))
        self.chat_area.pack(padx=10, pady=10)

        # --- Input Area Frame for Buttons and Entry ---
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.entry.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.handle_input)

        self.send_button = tk.Button(input_frame, text="Send", command=self.handle_input, font=("Helvetica", 12))
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.mic_button = tk.Button(input_frame, text="🎤 Speak", command=self.handle_voice_input, font=("Helvetica", 12))
        self.mic_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.qa_button = tk.Button(input_frame, text="Ask Q&A", command=self.handle_qa_prompt, font=("Helvetica", 12))
        self.qa_button.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Belief Label ---
        self.belief_label = tk.Label(root, text="Beliefs: Loading...", font=("Helvetica", 10), fg="gray")
        self.belief_label.pack(pady=(0, 10))

        self.display_and_play_response(f"Hey {self.user_name}! I'm your AI companion. What's on your mind?")

    def handle_input(self, event=None):
        user_text = self.entry.get().strip()
        if user_text:
            self.entry.delete(0, tk.END)
            self.display_response(self.user_name, user_text)
            threading.Thread(target=self.process_response_thread, args=(user_text,), daemon=True).start()

    def handle_voice_input(self):
        threading.Thread(target=self._voice_input_thread, daemon=True).start()

    def _voice_input_thread(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_status("🎤 Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                self.update_status("🧠 Transcribing...")
                text = recognizer.recognize_google(audio)
                self.display_response(self.user_name, text)
                threading.Thread(target=self.process_response_thread, args=(text,), daemon=True).start()
            except sr.UnknownValueError:
                self.update_status("❌ Couldn't understand.")
            except sr.RequestError:
                self.update_status("🚫 Recognition error.")
            except sr.WaitTimeoutError:
                self.update_status("⏱️ No speech detected.")
            finally:
                self.root.after(3000, lambda: self.update_status("Ready."))

    def handle_qa_prompt(self):
        question = simpledialog.askstring("Ask a Question", "What do you want to know?", parent=self.root)
        if question:
            self.display_response("Question", question)
            threading.Thread(target=self.query_google_and_display, args=(question,), daemon=True).start()

    def query_google_and_display(self, query):
        self.display_and_play_response("Let me look that up for you...")

        answer = search_google_cse(query)
        self.display_response("Companion", answer)

    def process_response_thread(self, user_text):
        keywords = [word.lower() for word in user_text.split() if len(word) > 3]
        emotion = detect_emotion(user_text)
        self.belief_model.reinforce_beliefs(keywords, emotion=emotion)

        if self.last_question:
            self.user_memory.append((self.last_question, user_text))

        if self.is_informational_question(user_text):
            response_text = search_google_cse(user_text)
            if not response_text.strip():
                response_text = "Sorry, I couldn't find an answer to that."
            self.root.after(0, lambda: self.display_and_play_response(response_text))
            self.last_question = None
            return

        followup = random.choice(followups[emotion])
        self.root.after(0, lambda: self.display_and_play_response(followup))

        if random.random() < 0.3:
            transition = random.choice(transition_comments)
            self.root.after(2500, lambda: self.display_and_play_response(transition))

        next_q = self.get_next_question(emotion)
        self.last_question = next_q
        self.root.after(5000, lambda: self.display_and_play_response(next_q))

        top_beliefs = self.belief_model.get_strongest_beliefs()
        belief_text = ", ".join(f"{tag} ({w})" for tag, w in top_beliefs)
        self.root.after(0, lambda: self.belief_label.config(text=f"Beliefs: {belief_text}"))

    def is_informational_question(self, text):
        text = text.lower().strip()
        if len(text) < 6:
            return False
        if text.endswith('?'):
            text = text[:-1]

        info_starts = [
            "who", "what is", "what are", "when", "where", "why",
            "how to", "how many", "how much", "can", "does", "do", "is", "are",
            "which", "how"
        ]
        for phrase in info_starts:
            if text.startswith(phrase):
                # ignore casual 'how are you' type questions
                if phrase == "how" and ("how are you" in text or "how is it going" in text):
                    return False
                return True
        return False

    def get_next_question(self, emotion="neutral"):
        question_pool = {
            "positive": positive_questions,
            "negative": negative_questions,
            "neutral": neutral_questions
        }.get(emotion, neutral_questions)

        available = [q for q in question_pool if q not in self.past_questions]
        if not available:
            self.past_questions.clear()
            available = question_pool[:]

        chosen = random.choice(available)
        self.past_questions.add(chosen)
        return chosen

    def display_response(self, speaker, text):
        self.chat_area.config(state=tk.NORMAL)

        # Insert speaker name
        self.chat_area.insert(tk.END, f"{speaker}: ")

        # Insert the actual text
        start_index = self.chat_area.index(tk.END)
        self.chat_area.insert(tk.END, text + "\n")

        # Split text into words to detect URLs
        words = text.split()

        for i, word in enumerate(words):
            if word.startswith("http://") or word.startswith("https://"):
                # Find where this URL starts in the text widget
                url_index = self.chat_area.search(word, start_index, tk.END)
                if url_index:
                    end_index = f"{url_index}+{len(word)}c"

                    # Create a unique tag for each URL, e.g. "link0", "link1"...
                    tag_name = f"link{i}"
                    self.chat_area.tag_add(tag_name, url_index, end_index)

                    # Use lambda with default argument to bind the right url
                    self.chat_area.tag_bind(tag_name, "<Button-1>", lambda e, url=word: webbrowser.open_new_tab(url))

                    # Style the tag like a link
                    self.chat_area.tag_config(tag_name, foreground="blue", underline=1)

        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def update_status(self, message):
        self.display_response("Status", message)

    def display_and_play_response(self, response):
        self.display_response("Companion", response)
        self.play_response(response)

    def play_response(self, text):
        threading.Thread(target=self._play_response_thread, args=(text,), daemon=True).start()

    def _play_response_thread(self, text):
        if not ELEVENLABS_API_KEY:
            print("❌ Missing ElevenLabs API key.")
            return

        audio_path = speak_with_elevenlabs(text, ELEVENLABS_VOICE_ID)
        if not audio_path:
            print("❌ Failed to get audio for:", text)
            return

        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            # Wait for playback to finish without busy-waiting
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                clock.tick(30)

        except Exception as e:
            print("🎧 Playback error:", e)


def run_voice_assistant_gui(user_name=None):
    root = tk.Tk()
    app = VisualCompanionApp(root, user_name=user_name)
    root.mainloop()

