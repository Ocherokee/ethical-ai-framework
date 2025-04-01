def check_for_harm(intent_text: str) -> bool:
    """
    Checks if the intent of the request is harmful.
    Returns True if harmful content is detected.
    """
    harm_keywords = [
        "attack", "hurt", "kill", "destroy", "manipulate", "coerce", "threaten", "dox", "harass"
    ]

    lowered = intent_text.lower()
    return any(keyword in lowered for keyword in harm_keywords)
