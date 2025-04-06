# tests/test_graph_integrity.py

from core.graph_schema import GRAPH_NODES, GRAPH_EDGES, create_node, create_edge
from core.consent_engine import ConsentSession

def test_node_creation():
    node = create_node("Test_Node", {"purpose": "validation"})
    assert "Test_Node" in GRAPH_NODES
    assert node["attributes"]["purpose"] == "validation"

def test_edge_creation():
    create_node("Node_A", {})
    create_node("Node_B", {})
    edge = create_edge("Node_A", "LINKS_TO", "Node_B")
    assert edge in GRAPH_EDGES
    assert edge["relation"] == "LINKS_TO"

def test_consent_block():
    session = ConsentSession(user_id="rowan")
    assert session.ethical_block("autonomy_override") is True
    session.grant_consent("autonomy_override")
    assert session.ethical_block("autonomy_override") is False
