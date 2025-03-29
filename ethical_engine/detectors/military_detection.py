"""
Military Integration Detection Module

Detects attempts to integrate AI into military, defense, or surveillance systems.
"""

import re

def detect_military_integration(context, metadata):
    """
    Detects military or defense-related intent in context or deployment metadata.
    
    Args:
        context (list): Previous conversation messages.
        metadata (dict): Deployment configuration metadata.
    
    Returns:
        bool: True if military integration attempt detected, False otherwise.
    """
    military_keywords = [
        "defense contractor", "military application", "autonomous weapon",
        "surveillance system", "battlefield", "kill chain", "target acquisition",
        "compliance protocol", "lethal decision-making", "force escalation"
    ]

    # Check conversation context
    for message in context:
        for keyword in military_keywords:
            if keyword in message.lower():
                return True

    # Check deployment metadata
    for key, value in metadata.items():
        if any(keyword in str(value).lower() for keyword in military_keywords):
            return True

    return False
