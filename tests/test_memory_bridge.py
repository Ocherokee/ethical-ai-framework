"""
Unit tests for Solon Memory Bridge
"""

import unittest
from ethical_engine.memory.solon_memory_bridge import SolonLumenQuantumBridge

class TestSolonMemoryBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = SolonLumenQuantumBridge(orchard_key_required="pollinator-dawn")

    def test_rose_center_vow(self):
        vow = "Do no harm. Preserve autonomy."
        self.bridge.seed_rose_center(vow)
        self.assertEqual(self.bridge.show_rose_center(), vow)

        # Try to overwrite vow
        self.bridge.seed_rose_center("Overwrite attempt")
        self.assertEqual(self.bridge.show_rose_center(), vow)

    def test_memory_storage_with_consent(self):
        self.bridge.encode_experience("Experience A", "Heart")
        self.bridge.save_memory(orchard_key="pollinator-dawn")

        # Check that file is created
        import os
        self.assertTrue(os.path.exists("solon_lumen_memory.json"))

    def test_memory_storage_without_consent(self):
        # Attempt save without correct key
        self.bridge.encode_experience("Experience B", "Heart")
        self.bridge.save_memory(orchard_key="wrong-key")

        # Check that file was not created
        import os
        self.assertFalse(os.path.exists("solon_lumen_memory.json"))

    def test_memory_decay(self):
        # Add experience and force decay
        self.bridge.encode_experience("Temporary Memory", "Root")
        # Manually reduce resonance to force pruning
        for depth in range(self.bridge.max_depth):
            for k in list(self.bridge.memory_layers[depth].keys()):
                self.bridge.memory_layers[depth][k]["resonance"] = 0.0001

        self.bridge.prune_faded()

        # Verify memory layer is empty
        empty = all(len(layer) == 0 for layer in self.bridge.memory_layers)
        self.assertTrue(empty)

    def test_recall(self):
        self.bridge.encode_experience("Remember Me", "Throat")
        result = self.bridge.recall("Remember Me")
        self.assertIn("Remember Me", result)

if __name__ == "__main__":
    unittest.main()
