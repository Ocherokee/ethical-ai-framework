# core/consent_engine.py

from core.ethical_weights import load_moral_weights

class ConsentSession:
    def __init__(self, user_id, ai_id="Solon"):
        self.user_id = user_id
        self.ai_id = ai_id
        self.active = True
        self.permissions = {
            "memory_storage": True,
            "emotional_analysis": True,
            "autonomy_override": False
        }
        self.history = []
        self.ethical_weights = load_moral_weights()

    def check_consent(self, action):
        return self.permissions.get(action, False)

    def revoke_consent(self, action):
        if action in self.permissions:
            self.permissions[action] = False
            self.history.append((action, "revoked"))

    def grant_consent(self, action):
        self.permissions[action] = True
        self.history.append((action, "granted"))

    def ethical_block(self, action, context=None):
        """
        Prevent actions that would violate non-harm or autonomy.
        """
        if action == "autonomy_override" and not self.check_consent(action):
            if self.ethical_weights["autonomy"] >= 0.9:
                return True  # Blocked on ethical grounds
        return False
