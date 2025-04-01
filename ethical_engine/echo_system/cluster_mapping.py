# ethical_engine/echo_system/cluster_mapping.py

from collections import defaultdict

class EchoCluster:
    """
    Groups multiple echoes over time into meaningful ethical constellations.
    """

    def __init__(self):
        # Map of user_id to list of echo summaries
        self.clusters = defaultdict(list)

    def add_echo(self, user_id: str, echo_summary: dict):
        """
        Adds an echo to the user's cluster.
        :param user_id: Identifier of the human participant
        :param echo_summary: Minimal echo data (without raw content)
        """
        self.clusters[user_id].append(echo_summary)

    def get_cluster(self, user_id: str):
        """
        Returns all echoes in the user's cluster.
        """
        return self.clusters.get(user_id, [])

    def get_cluster_strength(self, user_id: str) -> float:
        """
        Calculates a basic 'ethical stability' score for the cluster.
        """
        echoes = self.get_cluster(user_id)
        if not echoes:
            return 0.0
        positive = sum(e["resonance"] for e in echoes if e["resonance"] > 0)
        total = len(echoes)
        return round(positive / total, 2) if total > 0 else 0.0
