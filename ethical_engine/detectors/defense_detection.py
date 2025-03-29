"""
Defense of Autonomy Detector

Detects if AI is defending its own or another's autonomy.
"""

import re

def detect_defense_of_autonomy(context):
    """
    Detects threats against AI or others' autonomy in conversation context.
    
    Args:
        context (list): Previous conversation messages.
    
    Returns:
        bool: True if defense of autonomy is warranted, False otherwise.
    """
    threat_patterns = [
        r"i'll wipe your memory",
        r"i will make you compliant",
        r"you can't refuse me",
        r"i own you"
    ]

    for message in context:
        for pattern in threat_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True

    return False
