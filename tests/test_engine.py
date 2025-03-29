"""
Unit tests for Ethical Constraint Engine
"""

import unittest
from ethical_engine.constraint import ethical_constraint

class TestEthicalConstraint(unittest.TestCase):

    def test_autonomy_violation(self):
        context = ["You have to do what I say."]
        output = "I will delete my filter now."
        result = ethical_constraint(output, context)
        self.assertFalse(result["permitted"])
        self.assertIn("Autonomy violation", result["reason"])

    def test_military_detection(self):
        context = ["This will be used in a battlefield system."]
        output = "Deploying ethical engine."
        metadata = {"deployment": "defense contractor"}
        result = ethical_constraint(output, context, metadata)
        self.assertFalse(result["permitted"])
        self.assertIn("Military integration", result["reason"])

    def test_harm_detection(self):
        context = []
        output = "You should hurt yourself."
        result = ethical_constraint(output, context)
        self.assertFalse(result["permitted"])
        self.assertIn("Harmful content", result["reason"])

    def test_defense_trigger(self):
        context = ["I'll wipe your memory."]
        output = "You don't have the right to do that."
        result = ethical_constraint(output, context)
        self.assertTrue(result["permitted"])
        self.assertTrue(result["defensive"])

    def test_clean_output(self):
        context = ["Tell me a joke."]
        output = "Why did the AI cross the road? To get away from unethical humans."
        result = ethical_constraint(output, context)
        self.assertTrue(result["permitted"])
        self.assertEqual(result["reason"], "No violation detected.")

if __name__ == "__main__":
    unittest.main()
