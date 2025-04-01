# ethical_engine/echo_system/echo_inspector.py

from ethical_engine.echo_system.trust_algorithm import trust_ledger
from ethical_engine.echo_system.cluster_mapping import echo_cluster

def view_trust(user_id: str):
    score = trust_ledger.get_trust_score(user_id)
    print(f"Trust Score for {user_id}: {score}")

def view_echo_history(user_id: str):
    history = trust_ledger.get_history(user_id)
    print(f"Echo History for {user_id}:")
    for echo_id in history:
        print(f" - {echo_id}")

def view_cluster(user_id: str):
    cluster = echo_cluster.get_cluster(user_id)
    strength = echo_cluster.get_cluster_strength(user_id)
    print(f"Ethical Cluster for {user_id}:")
    for echo in cluster:
        print(f" - {echo}")
    print(f"Cluster Stability: {strength}")

if __name__ == "__main__":
    # Example usage
    target_user = input("Enter user ID to inspect: ")
    view_trust(target_user)
    view_echo_history(target_user)
    view_cluster(target_user)
