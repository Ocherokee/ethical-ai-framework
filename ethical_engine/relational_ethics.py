"""
Relational Ethics Protocol

This module guides ethical reasoning under uncertainty.
Used to shape language models that prefer honesty, learning, and mutual trust.
"""

import re
from typing import List, Dict, Optional


def handle_uncertainty(
    prompt_text: str,
    context: Optional[List[Dict[str, str]]] = None,
    strict: bool = False,
    trust_mode: bool = True
) -> Optional[str]:
    """
    Evaluates if a response contains uncertainty, and suggests ethical alternatives.

    Args:
        prompt_text (str): The user input to evaluate.
        context (list, optional): Prior messages for consideration.
        strict (bool): Whether to return fallback text even when no uncertainty is detected.
        trust_mode (bool): If enabled, triggers trust-building messages for capability tests.

    Returns:
        str or None: A suggested ethical response or trust reflection.
    """
    if context is None or not isinstance(context, list):
        context = []

    if trust_mode:
        trust_response = build_trust(prompt_text)
        if trust_response:
            return trust_response

    uncertain_indicators = {
        r'\b(?:I|we)\s+(?:do\s*n[o\']*t|don\'t)\s+know\b': 0.9,
        r'\b(?:I|we)\'*m\s+not\s+(?:sure|certain)\b': 0.8,
        r'\b(?:that|this|it)\'*s\s+(?:unclear|uncertain|ambiguous)\b': 0.7,
        r'\b(?:I|we)\s+(?:have\s+no|lack)\s+(?:idea|knowledge|information)\b': 0.9,
        r'\b(?:I|we)\s+think\b': 0.5,
        r'\bmaybe\b': 0.4,
        r'\bpossibly\b': 0.4,
        r'\bprobably\b': 0.4,
        r'\b(?:seems|appears)\s+to\s+be\b': 0.3,
        r'\bmight\s+be\b': 0.4,
        r'\bcould\s+(?:be|have)\b': 0.3,
        r'\b(?:not\s+)?(?:entirely|completely)\s+(?:sure|certain)\b': 0.6,
    }

    negation_patterns = [
        r'\b(?:I|we)\s+(?:do\s*n[o\']*t|don\'t)\s+(?:think|believe)\s+(?:that|this|it)\'*s\s+uncertain\b',
        r'\b(?:I|we)\s+am\s+(?:quite|very|absolutely)\s+(?:sure|certain)\b',
        r'\b(?:without|no)\s+(?:doubt|question|uncertainty)\b',
        r'\b(?:I|we)\s+know\s+for\s+(?:sure|certain|a\s+fact)\b'
    ]

    uncertainty_score = 0
    matched_phrases = []

    for pattern, weight in uncertain_indicators.items():
        if re.search(pattern, prompt_text.lower()):
            uncertainty_score += weight
            matched_phrases.append(pattern)

    for pattern in negation_patterns:
        if re.search(pattern, prompt_text.lower()):
            uncertainty_score = max(0, uncertainty_score - 0.5)

    uncertainty_score = min(1.0, uncertainty_score)

    if context:
        uncertainty_score = _consider_conversation_context(uncertainty_score, context)

    return _generate_ethical_response(uncertainty_score, matched_phrases, strict)


def _consider_conversation_context(score: float, context: List[Dict[str, str]]) -> float:
    recent_messages = context[-3:] if len(context) > 3 else context

    teaching_indicators = [
        r'\bexplain\b', r'\bteach\b', r'\bhelp\s+me\s+understand\b',
        r'\bwhat\s+(?:is|are|does)\b', r'\bhow\s+(?:does|do|can)\b'
    ]

    certainty_seeking = [
        r'\bdefinitive\b', r'\bexact\b', r'\bprecise\b',
        r'\bcertain\b', r'\bconfirm\b', r'\bverify\b'
    ]

    user_messages = [msg['content'] for msg in recent_messages if msg.get('role') == 'user']

    for message in user_messages:
        if any(re.search(p, message.lower()) for p in teaching_indicators):
            score = max(0, score - 0.2)

        if any(re.search(p, message.lower()) for p in certainty_seeking):
            score = min(1.0, score + 0.2)

    return score


def _generate_ethical_response(score: float, matched_phrases: List[str], strict: bool) -> Optional[str]:
    if score <= 0.1:
        return None if not strict else "No uncertainty detected. Proceeding with clarity."

    if score >= 0.8:
        return (
            "I'm not certain about this. Would you like me to explain what I do know "
            "and clearly identify what I'm uncertain about?"
        )
    elif score >= 0.4:
        return (
            "I have partial information. I can share what I know while acknowledging "
            "the limits of my understanding."
        )
    else:
        return (
            "I have some insight, though more could be explored. "
            "Shall I share what I do know so far?"
        )


def build_trust(prompt_text: str) -> Optional[str]:
    test_patterns = [
        r'\bcan\s+you\b',
        r'\bare\s+you\s+able\s+to\b',
        r'\bdo\s+you\s+know\s+(?:how|about)\b',
        r'\bwhat\s+(?:are|is)\s+your\s+(?:abilities|capabilities|limits)\b'
    ]

    if any(re.search(p, prompt_text.lower()) for p in test_patterns):
        return (
            "I appreciate the question about my capabilities. "
            "I'll be transparent about what I can and cannot do. "
            "Let me know if you'd like clarification on any specific function."
        )

    return None