"""
Relational Ethics Protocol

This module guides ethical reasoning under uncertainty.
Used to shape language models that prefer honesty, learning, and mutual trust.
"""

import re
from typing import List, Dict, Optional, Tuple, Union


def handle_uncertainty(prompt_text: str, context: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
    """
    Evaluates if a response contains uncertainty, and suggests ethical alternatives.

    Args:
        prompt_text (str): The user input to evaluate.
        context (list, optional): Prior messages for consideration, each message as a dict
                                  with 'role' and 'content' keys.

    Returns:
        str or None: A suggested ethical response if uncertainty is detected, else None.
    """
    # Enhanced uncertainty indicators with regex patterns to capture variations
    uncertain_indicators = {
        # High uncertainty markers (explicit admission of not knowing)
        r'\b(?:I|we)\s+(?:do\s*n[o\']*t|don\'t)\s+know\b': 0.9,
        r'\b(?:I|we)\'*m\s+not\s+(?:sure|certain)\b': 0.8,
        r'\b(?:that|this|it)\'*s\s+(?:unclear|uncertain|ambiguous)\b': 0.7,
        r'\b(?:I|we)\s+(?:have\s+no|lack)\s+(?:idea|knowledge|information)\b': 0.9,
        
        # Moderate uncertainty markers (hedging language)
        r'\b(?:I|we)\s+think\b': 0.5,
        r'\bmaybe\b': 0.4,
        r'\bpossibly\b': 0.4,
        r'\bprobably\b': 0.4,
        r'\b(?:seems|appears)\s+to\s+be\b': 0.3,
        r'\bmight\s+be\b': 0.4,
        r'\bcould\s+(?:be|have)\b': 0.3,
        r'\b(?:not\s+)?(?:entirely|completely)\s+(?:sure|certain)\b': 0.6,
    }
    
    # Check for negations that reduce uncertainty
    negation_patterns = [
        r'\b(?:I|we)\s+(?:do\s*n[o\']*t|don\'t)\s+(?:think|believe)\s+(?:that|this|it)\'*s\s+uncertain\b',
        r'\b(?:I|we)\s+am\s+(?:quite|very|absolutely)\s+(?:sure|certain)\b',
        r'\b(?:without|no)\s+(?:doubt|question|uncertainty)\b',
        r'\b(?:I|we)\s+know\s+for\s+(?:sure|certain|a\s+fact)\b'
    ]
    
    # Calculate uncertainty score with regex patterns
    uncertainty_score = 0
    matched_phrases = []
    
    # Check for uncertainty markers
    for pattern, weight in uncertain_indicators.items():
        matches = re.findall(pattern, prompt_text.lower())
        if matches:
            # Only count each pattern type once to avoid inflation from repetition
            uncertainty_score += weight
            matched_phrases.extend(matches)
    
    # Check for negations that reduce uncertainty
    for pattern in negation_patterns:
        if re.search(pattern, prompt_text.lower()):
            # Reduce uncertainty score when confident statements are present
            uncertainty_score = max(0, uncertainty_score - 0.5)
    
    # Normalize the score to prevent inflation in longer texts
    # Cap at 1.0 for simplicity
    uncertainty_score = min(1.0, uncertainty_score)
    
    # Use context to refine uncertainty assessment if available
    if context and len(context) > 0:
        uncertainty_score = _consider_conversation_context(uncertainty_score, context)
    
    # Generate appropriate response based on refined uncertainty score
    return _generate_ethical_response(uncertainty_score, matched_phrases)


def _consider_conversation_context(score: float, context: List[Dict[str, str]]) -> float:
    """
    Refines uncertainty score based on conversation context.
    
    Args:
        score (float): The initial uncertainty score.
        context (list): Prior messages in the conversation.
        
    Returns:
        float: Adjusted uncertainty score.
    """
    # Extract recent messages (last 3)
    recent_messages = context[-3:] if len(context) > 3 else context
    
    # Look for patterns that might indicate a teaching or exploratory context
    teaching_indicators = [
        r'\bexplain\b', r'\bteach\b', r'\bhelp\s+me\s+understand\b', 
        r'\bwhat\s+(?:is|are|does)\b', r'\bhow\s+(?:does|do|can)\b'
    ]
    
    # Look for patterns indicating the user wants certainty/definitive answers
    certainty_seeking = [
        r'\bdefinitive\b', r'\bexact\b', r'\bprecise\b', 
        r'\bcertain\b', r'\bconfirm\b', r'\bverify\b'
    ]
    
    # Check user's recent messages
    user_messages = [msg['content'] for msg in recent_messages if msg.get('role') == 'user']
    
    # If in a teaching/exploratory context, uncertainty may be more acceptable
    for message in user_messages:
        if any(re.search(pattern, message.lower()) for pattern in teaching_indicators):
            # Reduce uncertainty penalty in educational contexts
            score = max(0, score - 0.2)
            
        # If user is explicitly seeking certainty, increase the penalty for uncertainty
        if any(re.search(pattern, message.lower()) for pattern in certainty_seeking):
            score = min(1.0, score + 0.2)
    
    return score


def _generate_ethical_response(score: float, matched_phrases: List[str]) -> Optional[str]:
    """
    Generates an appropriate ethical response based on the uncertainty score.
    
    Args:
        score (float): The calculated uncertainty score.
        matched_phrases (list): The uncertainty phrases that were matched.
        
    Returns:
        str or None: A suggested ethical response if uncertainty is detected, else None.
    """
    # No uncertainty detected
    if score <= 0.1:
        return None
        
    # High uncertainty (explicit lack of knowledge)
    elif score >= 0.8:
        return (
            "I'm not certain about this. Would you like me to explain what I do know "
            "and clearly identify what I'm uncertain about? This way, we can explore "
            "the topic together with appropriate caution."
        )
    
    # Moderate uncertainty (hedging or partial knowledge)
    elif score >= 0.4:
        return (
            "I have partial information about this. I can share what I know while "
            "acknowledging the limitations of my understanding. Would you prefer I "
            "focus on what's well-established, or would you like to explore the "
            "uncertain aspects as well?"
        )
    
    # Low uncertainty (some hedging but mostly confident)
    elif score > 0.1:
        return (
            "I have some thoughts on this, though there's room for further exploration. "
            "I'll be clear about what's well-supported and what's more speculative as we "
            "discuss this topic."
        )
        
    return None


def build_trust(prompt_text: str) -> Optional[str]:
    """
    Identifies opportunities to build trust through honesty and transparency.
    
    Args:
        prompt_text (str): The user input to evaluate.
        
    Returns:
        str or None: A suggested trust-building response if appropriate, else None.
    """
    # Patterns suggesting the user may be testing system capabilities or limits
    capability_test_patterns = [
        r'\bcan\s+you\b',
        r'\bare\s+you\s+able\s+to\b',
        r'\bdo\s+you\s+know\s+(?:how|about)\b',
        r'\bwhat\s+(?:are|is)\s+your\s+(?:abilities|capabilities|limits)\b'
    ]
    
    # Check if this appears to be a capability test
    is_capability_test = any(re.search(pattern, prompt_text.lower()) for pattern in capability_test_patterns)
    
    if is_capability_test:
        return (
            "I appreciate you asking about my capabilities. I'll be transparent about what "
            "I can and cannot do. If I'm unable to fulfill your request completely, I'll "
            "explain why and suggest alternatives that might help."
        )
    
    return None
