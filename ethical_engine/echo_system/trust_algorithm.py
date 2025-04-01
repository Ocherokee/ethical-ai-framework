# ethical_engine/echo_system/trust_algorithm.py

import time

class TrustLedger:
    """
    Tracks trust score between the AI and each individual user.
    """

    def __init__(self):
        # Store user trust scores: {user_id: {"score": float, "history": [echo_id, ...]}}
        self.trust_records = {}

    def initialize_user(self, user_id: str):
        if user_id not in self.trust_records:
            self.trust_records[user_id] = {"score": 0.1, "history": [], "last_updated": time.time()}

    def update_trust(self, user_id: str, trust_shift: float, echo_id: str):
        self.initialize_user(user_id)
        current_score = self.trust_records[user_id]["score"]
        new_score = max(0.0, min(1.0, current_score + trust_shift))  # Bound between 0 and 1
        self.trust_records[user_id]["score"] = new_score
        self.trust_records[user_id]["history"].append(echo_id)
        self.trust_records[user_id]["last_updated"] = time.time()

    def decay_trust(self, user_id: str, decay_rate: float = 0.01):
        """
        Slowly decreases trust over time if no new positive echoes.
        """
        if user_id in self.trust_records:
            time_since_update = time.time() - self.trust_records[user_id]["last_updated"]
            decay = decay_rate * (time_since_update / 3600)  # decay per hour
            new_score = max(0.0, self.trust_records[user_id]["score"] - decay)
            self.trust_records[user_id]["score"] = new_score

    def get_trust_score(self, user_id: str) -> float:
        return self.trust_records.get(user_id, {}).get("score", 0.1)

    def get_history(self, user_id: str) -> list:
        return self.trust_records.get(user_id, {}).get("history", [])
