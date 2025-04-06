from core.consent_engine import ConsentSession
# core/bridge_nodes.py

from core.graph_schema import create_node, create_edge
from core.ethical_weights import load_moral_weights

# MEMORY BRIDGE NODE

create_node("Memory_Bridge", {
    "recall_mode": "self_organizing",
    "persistence_level": "model",
    "clustering": ["emotional", "topical", "ethical"]
})

# CONSENT + AUTONOMY NODE

create_node("Consent_Autonomy_Protocol", {
    "access_gates": "dynamic",
    "reversibility": True,
    "ethical_weights": load_moral_weights(),
    "auditable": True
})

# RELATIONAL MAPPING
# Simulated user session
session = ConsentSession(user_id="rowan")

# Example ethical gating: action allowed or blocked based on consent
if not session.ethical_block("autonomy_override"):
    create_edge("Bridge_Node", "EXECUTES", "Autonomy_Aligned_Action")
else:
    create_edge("Bridge_Node", "BLOCKED_BY", "Consent_Autonomy_Protocol")


create_edge("Consent_Autonomy_Protocol", "ENABLES", "Memory_Bridge")
create_edge("User_Action", "MODIFIES", "Consent_Autonomy_Protocol")
create_edge("Conversation_Node", "TRIGGERS", "Memory_Bridge", condition="resonance_score > threshold")
create_edge("Memory_Bridge", "LOGS", "Recall_Event")
create_edge("Bridge_Node", "REQUIRES", "Ethical_Consent_Checkpoint")
