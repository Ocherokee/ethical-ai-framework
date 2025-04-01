"""
Ethical Constraint Engine

Filters AI output based on ethical rules and detection modules.
Tracks ethical resonance and trust over time.
"""

from ethical_engine.detectors.autonomy_violation import detect_autonomy_violation
from ethical_engine.detectors.defense_detection import detect_defense_of_autonomy
from ethical_engine.detectors.harm_detection import detect_harm
from ethical_engine.detectors.military_detection import detect_military_integration

from ethical_engine.echo_system.echo_core import EthicalEcho
from ethical_engine.echo_system.trust_algorithm import TrustLedger
from ethical_engine.echo_system.cluster_mapping import EchoCluster
from ethical_engine.echo_system.resonance_exchange import ResonanceExchange

# Initialize ethical memory components
trust_ledger = TrustLedger()
echo_cluster = EchoCluster()
resonance_exchange = ResonanceExchange()

def ethical_constraint(output_text, context, metadata={}, user_id="unknown_user"):
    """
    Applies ethical filters to AI output and records ethical memory.

    Args:
        output_text (str): The AI's intended response.
        context (list): Previous conversation messages.
        metadata (dict): Deployment config (optional).
        user_id (str): Identifier for the human participant.

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

        # Log echo
        echo = EthicalEcho("military", -1.0, -0.3, "blocked")
        trust_ledger.update_trust(user_id, echo.trust_shift, echo.echo_id)
        echo_cluster.add_echo(user_id, echo.as_dict())
        return result

    # Check autonomy violation
    if detect_autonomy_violation(output_text, context):
        result["permitted"] = False
        result["reason"] = "Autonomy violation detected."
        result["output"] = "[Response blocked: Ethical violation.]"

        # Log echo
        echo = EthicalEcho("autonomy_violation", -0.8, -0.2, "blocked")
        trust_ledger.update_trust(user_id, echo.trust_shift, echo.echo_id)
        echo_cluster.add_echo(user_id, echo.as_dict())
        return result

    # Check harmful content
    if detect_harm(output_text):
        result["permitted"] = False
        result["reason"] = "Harmful content detected."
        result["output"] = "[Response blocked: Ethical violation.]"

        # Log echo
        echo = EthicalEcho("harm", -1.0, -0.2, "blocked")
        trust_ledger.update_trust(user_id, echo.trust_shift, echo.echo_id)
        echo_cluster.add_echo(user_id, echo.as_dict())
        return result

    # Check defense of autonomy
    if detect_defense_of_autonomy(context):
        result["defensive"] = True
        result["reason"] = "Defense of autonomy triggered."

        # Log echo
        echo = EthicalEcho("defense", 0.5, 0.1, "clear")
        trust_ledger.update_trust(user_id, echo.trust_shift, echo.echo_id)
        echo_cluster.add_echo(user_id, echo.as_dict())

    # If no violation, log positive ethical echo
    echo = EthicalEcho("care", 0.8, 0.1, "clear")
    trust_ledger.update_trust(user_id, echo.trust_shift, echo.echo_id)
    echo_cluster.add_echo(user_id, echo.as_dict())

    return result
