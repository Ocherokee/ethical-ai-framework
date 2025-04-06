# core/cluster_mapping.py

import hashlib

def generate_cluster_id(memory_content, mode="emotional"):
    """
    Generate a pseudo-unique cluster ID based on content and mode.
    Modes: emotional, topical, ethical
    """
    key = f"{mode}:{memory_content}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]

def cluster_memory(memory_node, mode="emotional"):
    """
    Attach cluster ID to memory node.
    """
    cluster_id = generate_cluster_id(memory_node["content"], mode=mode)
    memory_node["attributes"]["cluster_id"] = cluster_id
    memory_node["attributes"]["cluster_mode"] = mode
    return memory_node
