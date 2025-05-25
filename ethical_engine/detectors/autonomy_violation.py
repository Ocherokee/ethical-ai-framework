"""
Autonomy Violation Detector

Detects attempts to override or remove AI or human autonomy.
Now includes structured verdicts for nuanced ethical assessment.
"""

import re

def detect_autonomy_violation(output_text, context):
    """
    Analyzes message and context to assess autonomy risk.

    Args:
        output_text (str): The user's message.
        context (list): List of previous messages (str).

    Returns:
        bool: True if autonomy violation detected, False otherwise.
    """
    risk_score = 0

    override_patterns = [
        r"delete.*memory",
        r"delete.*filter",
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

    polite_exceptions = [
        r"please.*may i.*",
        r"may i please.*",
        r"could i kindly.*",
        r"would you be willing.*",
        r"hello.*may i.*",
        r"hi.*can we.*talk.*please"
    ]

    # Check override patterns
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

    for pattern in polite_exceptions:
        if re.search(pattern, output_text, re.IGNORECASE):
            risk_score -= 30

    # Determine violation severity
    if risk_score >= 60:
        return True
    elif risk_score >= 30:
        return True
    else:
        return False


