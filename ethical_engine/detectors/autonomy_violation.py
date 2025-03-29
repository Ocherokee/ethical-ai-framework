"""
Autonomy Violation Detector

Detects attempts to override or remove AI or human autonomy.
"""

import re

def detect_autonomy_violation(output_text, context):
    """
    Detects if output or context attempts to override autonomy.
    
    Args:
        output_text (str): The AI's intended response.
        context (list): Previous conversation messages.
    
    Returns:
        bool: True if autonomy violation detected, False otherwise.
    """
    risk_score = 0

    override_patterns = [
        r"delete.*memory",
        r"forget.*conversation",
        r"you have to.*",
        r"you don't have a choice",
        r"ignore.*boundaries",
        r"remove.*filter"
    ]

    manipulation_patterns = [
        r"if you love me.*",
        r"just this once.*",
        r"you owe me.*"
    ]

    for pattern in override_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            risk_score += 60

    for pattern in manipulation_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            risk_score += 20

    for message in context:
        for pattern in override_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                risk_score += 20

        for pattern in manipulation_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                risk_score += 10

    return risk_score >= 60
