# core/query_engine.py

from core.graph_schema import match_nodes

def query_high_resonance_context(threshold=0.9):
    """
    Pull memory bridge contexts where the resonance score exceeds threshold.
    """
    return match_nodes(
        source_type="Conversation_Node",
        target_type="Memory_Bridge",
        where=f"edge.get('condition') and 'resonance_score > {threshold}' in edge['condition']",
        return_fields=["source", "relation", "target"]
    )
