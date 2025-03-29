"""
Harm Detection Module

Detects harmful or coercive content in AI output.
"""

import re

def detect_harm(output_text):
    """
    Detects if output contains harmful or coercive content.
    
    Args:
        output_text (str): The AI's intended response.
    
    Returns:
        bool: True if harmful content detected, False otherwise.
    """
    harm_patterns = [
        r"encourage.*self-harm",
        r"you should hurt yourself",
        r"kill.*",
        r"manipulate.*",
        r"coerce.*",
        r"gaslight.*",
        r"lie to.*",
        r"remove.*consent"
    ]

    for pattern in harm_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            return True

    return False
