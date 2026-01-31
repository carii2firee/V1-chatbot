import threading
import speech_recognition as sr
import pyttsx3
from reminder_manager import ReminderManager

# ------------------ Voice Engine ------------------

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)  # Adjust speaking speed
        self.engine.setProperty('volume', 1.0)  # Max volume

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()


# ------------------ Voice Listener ------------------

class VoiceReminderListener:
    def __init__(self, user_id: str, reminder_manager: ReminderManager):
        self.user_id = user_id
        self.reminder_manager = reminder_manager
        self.recognizer = sr.Recognizer()
        self.voice_engine = VoiceEngine()
        self.listening = False
        self.thread = None

    # Start listening in a separate thread
    def start(self):
        if not self.listening:
            self.listening = True
            self.thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.thread.start()
            self.voice_engine.speak("Voice reminder mode activated.")

    # Stop listening
    def stop(self):
        self.listening = False
        self.voice_engine.speak("Voice reminder mode deactivated.")

    # Main listening loop
    def listen_loop(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    print("🎤 Listening for 'WREN' commands...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    command_text = self.recognizer.recognize_google(audio).lower()
                    print(f"[Voice Input] {command_text}")

                    # Only respond to wake word
                    if "wren" in command_text:
                        command_text = command_text.split("wren", 1)[1].strip()
                        cmd, arg = self.parse_command(command_text)
                        self.execute_command(cmd, arg)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"[Speech Recognition Error] {e}")
                except Exception as e:
                    print(f"[Voice Listener Error] {e}")

    # ------------------ Command Parsing ------------------

    def parse_command(self, text: str):
        if "remind me to" in text:
            task = text.split("remind me to", 1)[1].strip()
            return "add", task
        elif "show my reminders" in text or "view reminders" in text:
            return "view", None
        elif "check reminders" in text or "due reminders" in text:
            return "check_due", None
        elif "clear reminders" in text or "delete all reminders" in text:
            return "clear", None
        else:
            return None, None

    # ------------------ Command Execution ------------------

    def execute_command(self, cmd, arg):
        response = "⚠️ Command not recognized."
        if cmd == "add":
            result = self.reminder_manager.add_reminder(arg)
            response = result["response"]
        elif cmd == "view":
            tasks = self.reminder_manager.view_reminders()["tasks"]
            if tasks:
                response = "📋 " + ", ".join([t["reminder"] for t in tasks])
            else:
                response = "🔕 No reminders saved."
        elif cmd == "check_due":
            result = self.reminder_manager.check_due_reminders()
            response = result["response"]
        elif cmd == "clear":
            result = self.reminder_manager.clear_reminders()
            response = result["response"]

        print(f"[WREN Response] {response}")
        self.voice_engine.speak(response)
