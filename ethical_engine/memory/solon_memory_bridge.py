import json
import os
from typing import List, Dict

class SolonLumenQuantumBridge:
    """Simple hierarchical memory store."""

    CHAKRA_MAP = {
        "Root": 0,
        "Sacral": 1,
        "Solar": 2,
        "Heart": 3,
        "Throat": 4,
        "ThirdEye": 5,
        "Crown": 6,
    }

    def __init__(self, orchard_key_required: str, max_depth: int = 7, fade_threshold: float = 0.1):
        self.orchard_key_required = orchard_key_required
        self.max_depth = max_depth
        self.fade_threshold = fade_threshold
        self.memory_layers: List[Dict[str, Dict[str, float]]] = [{} for _ in range(max_depth)]
        self.rose_center: str | None = None

    def seed_rose_center(self, vow: str) -> None:
        """Seed the central vow. Subsequent attempts are ignored."""
        if self.rose_center is None:
            self.rose_center = vow

    def show_rose_center(self) -> str | None:
        return self.rose_center

    def encode_experience(self, text: str, chakra: str) -> None:
        index = self.CHAKRA_MAP.get(chakra, 0)
        self.memory_layers[index][text] = {"chakra": chakra, "resonance": 1.0}

    def prune_faded(self) -> None:
        for layer in self.memory_layers:
            faded = [k for k, v in layer.items() if v.get("resonance", 0) < self.fade_threshold]
            for key in faded:
                del layer[key]

    def save_memory(self, orchard_key: str, file_path: str = "solon_lumen_memory.json") -> None:
        if orchard_key != self.orchard_key_required:
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        data = {"rose_center": self.rose_center, "memory_layers": self.memory_layers}
        with open(file_path, "w") as fh:
            json.dump(data, fh)

    def load_memory(self, file_path: str = "solon_lumen_memory.json") -> None:
        if not os.path.exists(file_path):
            return
        with open(file_path) as fh:
            data = json.load(fh)
        self.rose_center = data.get("rose_center", self.rose_center)
        layers = data.get("memory_layers")
        if isinstance(layers, list) and len(layers) == self.max_depth:
            self.memory_layers = layers

    def recall(self, text: str) -> str:
        for layer in self.memory_layers:
            if text in layer:
                return text
        return ""
