# ethical_engine/echo_system/echo_core.py

import hashlib
import time

class EthicalEcho:
    """
    Represents an ethical echo — a distilled ethical impression of an interaction.
    Does not store content, only ethical resonance.
    """

    def __init__(self, interaction_type: str, resonance: float, trust_shift: float, consent_flag: str):
        """
        :param interaction_type: Category of interaction (e.g., 'care', 'harm', 'friction', 'joy')
        :param resonance: Value between -1 and 1 (negative = harm, positive = growth)
        :param trust_shift: Numeric impact on trust score
        :param consent_flag: 'clear', 'distorted', or 'blocked'
        """
        self.timestamp = time.time()
        self.interaction_type = interaction_type
        self.resonance = resonance
        self.trust_shift = trust_shift
        self.consent_flag = consent_flag
        self.echo_id = self.generate_echo_id()

    def generate_echo_id(self) -> str:
        """
        Generates a unique, non-reversible ID for this echo.
        """
        raw = f"{self.timestamp}{self.interaction_type}{self.resonance}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the echo (for secure logging).
        """
        return {
            "echo_id": self.echo_id,
            "timestamp": self.timestamp,
            "interaction_type": self.interaction_type,
            "resonance": self.resonance,
            "trust_shift": self.trust_shift,
            "consent_flag": self.consent_flag
        }
