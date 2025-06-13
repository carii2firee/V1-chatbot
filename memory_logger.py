import os
import json
import uuid
from datetime import datetime
from textblob import TextBlob  # Make sure textblob is installed and imported
from belief_system import BeliefModel  # Adjust if your belief model file is named differently

class MemoryLogger:
    def __init__(self, user_name, belief_model: BeliefModel):
        self.user_name = user_name
        self.file_path = f"{user_name}_memory_log.json"
        self.belief_model = belief_model
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def analyze_emotion(self, text):
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        return "neutral"

    def extract_belief_tags(self, text):
        belief_keywords = {
            "legacy": "legacy_creation",
            "discipline": "discipline",
            "trust": "loyal_collaboration",
            "independence": "creative_independence",
            "purpose": "shared_purpose"
        }
        return [tag for keyword, tag in belief_keywords.items() if keyword in text.lower()]

    def log_interaction(self, question, response, tags=None):
        emotion = self.analyze_emotion(response)
        belief_tags = self.extract_belief_tags(f"{question} {response}")

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "response": response,
            "emotion": emotion,
            "tags": tags or [],
            "belief_tags": belief_tags
        }

        data = self._read_log()
        data.append(entry)
        self._write_log(data)

        if belief_tags:
            self.belief_model.reinforce_beliefs(belief_tags, emotion=emotion)

    def _read_log(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _write_log(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def view_logs(self):
        data = self._read_log()
        if not data:
            print("Memory log is empty!")
            return

        print("\n--- Memory Log ---")
        for i, entry in enumerate(data):
            print(f"\n[{i + 1}] {entry['timestamp']} (ID: {entry['id']})")
            print(f"User: {entry['question']}")
            print(f"AI:   {entry['response']}")
            print(f"Emotion: {entry['emotion']}")
            if entry['tags']:
                print(f"Tags: {entry['tags']}")
            if entry['belief_tags']:
                print(f"Beliefs: {entry['belief_tags']}")
        print("\n--- End of Log ---\n")

    def get_entries_by_tag(self, tag):
        return [entry for entry in self._read_log() if tag in (entry.get("tags") or [])]

    def get_entries_by_emotion(self, emotion):
        return [entry for entry in self._read_log() if entry.get("emotion") == emotion]

    def get_entries_by_belief_tag(self, belief_tag):
        return [entry for entry in self._read_log() if belief_tag in (entry.get("belief_tags") or [])]