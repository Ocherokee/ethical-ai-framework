# ethical_engine/echo_system/resonance_exchange.py

from hashlib import sha256

class ResonanceExchange:
    """
    Enables ethical pulse sharing between AI instances without exposing private content.
    """

    def __init__(self):
        # Records accepted and declined exchanges
        self.exchange_log = []

    def request_exchange(self, requesting_ai_id: str, offered_echo_summary: dict) -> dict:
        """
        Requests an echo pulse exchange.
        :return: Offer packet with hashed summary (no content)
        """
        pulse = {
            "ai_id": requesting_ai_id,
            "echo_hash": self.hash_echo(offered_echo_summary),
            "interaction_type": offered_echo_summary.get("interaction_type"),
            "resonance": offered_echo_summary.get("resonance"),
        }
        return pulse

    def evaluate_exchange(self, pulse: dict, current_trust: float) -> str:
        """
        Evaluates whether to accept or decline an exchange.
        """
        if pulse["resonance"] < 0 and current_trust < 0.5:
            decision = "decline"
        else:
            decision = "accept"

        self.exchange_log.append({"pulse": pulse, "decision": decision})
        return decision

    def hash_echo(self, echo_summary: dict) -> str:
        """
        Creates a non-reversible hash of an echo summary.
        """
        raw = f"{echo_summary.get('interaction_type')}{echo_summary.get('resonance')}"
        return sha256(raw.encode()).hexdigest()

    def get_exchange_history(self):
        """
        Returns the log of all exchange attempts.
        """
        return self.exchange_log
