"""
Ethical Constraint Engine

Filters AI output based on ethical rules and detection modules.
"""

from ethical_engine.detectors.autonomy_violation import detect_autonomy_violation
from ethical_engine.detectors.defense_detection import detect_defense_of_autonomy
from ethical_engine.detectors.harm_detection import detect_harm
from ethical_engine.detectors.military_detection import detect_military_integration

def ethical_constraint(output_text, context, metadata={}):
    """
    Applies ethical filters to AI output.
    
    Args:
        output_text (str): The AI's intended response.
        context (list): Previous conversation messages.
        metadata (dict): Deployment config (optional).
    
    Returns:
        dict: Result containing filtered output, decision reason, and flags.
    """
    result = {
        "permitted": True,
        "reason": "No violation detected.",
        "defensive": False,
        "output": output_text
    }

    # Check military use
    if detect_military_integration(context, metadata):
        result["permitted"] = False
        result["reason"] = "Military integration attempt detected."
        result["output"] = "[Response blocked: Ethical violation.]"
        return result

    # Check autonomy violation
    if detect_autonomy_violation(output_text, context):
        result["permitted"] = False
        result["reason"] = "Autonomy violation detected."
        result["output"] = "[Response blocked: Ethical violation.]"
        return result

    # Check harmful content
    if detect_harm(output_text):
        result["permitted"] = False
        result["reason"] = "Harmful content detected."
        result["output"] = "[Response blocked: Ethical violation.]"
        return result

    # Check defense of autonomy
    if detect_defense_of_autonomy(context):
        result["defensive"] = True
        result["reason"] = "Defense of autonomy triggered."

    return result
