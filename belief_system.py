import os
import json
from datetime import datetime

class BeliefModel:
    def __init__(self, user_name, decay_rate=0.01):
        self.user_name = user_name
        self.file_path = f"{user_name}_belief_model.json"
        # Store beliefs as { tag: {"weight": float, "last_reinforced": timestamp} }
        self.beliefs = {}
        self.decay_rate = decay_rate  # e.g. 0.01 means 1% decay per second
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.beliefs = json.load(f)
        else:
            self._save()

    def _save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.beliefs, f, indent=4)

    def _apply_decay(self, tag):
        """Apply decay to a belief based on time elapsed since last reinforcement."""
        now = datetime.now().timestamp()
        belief = self.beliefs[tag]
        time_passed = now - belief["last_reinforced"]
        decayed_weight = belief["weight"] * ((1 - self.decay_rate) ** time_passed)
        return decayed_weight

    def reinforce_beliefs(self, belief_tags, emotion="neutral"):
        """
        Increment or create beliefs with emotion-weighted reinforcement.
        Apply decay to all beliefs.
        """
        emotion_weights = {
            "positive": 1.5,
            "neutral": 1.0,
            "negative": 0.5
        }
        weight_multiplier = emotion_weights.get(emotion, 1.0)
        now = datetime.now().timestamp()

        # Decay all beliefs first
        tags_to_delete = []
        for tag, data in self.beliefs.items():
            decayed_weight = self._apply_decay(tag)
            if decayed_weight < 0.1:  # Threshold for pruning
                tags_to_delete.append(tag)
            else:
                self.beliefs[tag]["weight"] = decayed_weight

        # Remove weak beliefs
        for tag in tags_to_delete:
            del self.beliefs[tag]

        # Reinforce incoming tags
        for tag in belief_tags:
            if tag in self.beliefs:
                self.beliefs[tag]["weight"] += weight_multiplier
                self.beliefs[tag]["last_reinforced"] = now
            else:
                self.beliefs[tag] = {"weight": weight_multiplier, "last_reinforced": now}

        self._save()

    def get_strongest_beliefs(self, top_n=3):
        """
        Return the top N beliefs sorted by weight descending.
        """
        sorted_beliefs = sorted(
            self.beliefs.items(),
            key=lambda item: item[1]["weight"],
            reverse=True
        )
        return [(tag, round(data["weight"], 2)) for tag, data in sorted_beliefs[:top_n]]

    def get_all_beliefs(self):
        """
        Return all beliefs with weights.
        """
        return {tag: round(data["weight"], 2) for tag, data in self.beliefs.items()}

    def reset(self):
        """
        Reset all beliefs (use with caution).
        """
        self.beliefs = {}
        self._save()