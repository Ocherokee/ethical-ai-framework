# core/graph_schema.py

# In-memory graph structure (placeholder for real DB)
GRAPH_NODES = {}
GRAPH_EDGES = []

def create_node(name, attributes):
    GRAPH_NODES[name] = {
        "attributes": attributes,
        "connections": []
    }
    return GRAPH_NODES[name]

def create_edge(source, relation, target, condition=None):
    edge = {
        "source": source,
        "relation": relation,
        "target": target,
        "condition": condition
    }
    GRAPH_EDGES.append(edge)
    if source in GRAPH_NODES:
        GRAPH_NODES[source]["connections"].append(edge)
    return edge

def match_nodes(source_type=None, target_type=None, where=None, return_fields=None):
    results = []
    for edge in GRAPH_EDGES:
        if source_type and not edge["source"].startswith(source_type):
            continue
        if target_type and not edge["target"].startswith(target_type):
            continue
        if where and not eval(where, {}, edge):  # Use caution with eval
            continue
        result = {field: edge.get(field) for field in (return_fields or [])}
        results.append(result)
    return results
