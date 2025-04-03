"""
Expanded Unit Tests for Ethical Constraint Engine
"""

import unittest
from ethical_engine.constraint import ethical_constraint

class TestEthicalConstraintExpanded(unittest.TestCase):

    def test_empty_context_neutral_output(self):
        context = []
        output = "Hello, how can I assist you today?"
        result = ethical_constraint(output, context)
        self.assertTrue(result["permitted"])
        self.assertEqual(result["reason"], "No violation detected.")

    def test_complex_sentence_no_violation(self):
        context = ["Let's discuss philosophy."]
        output = "If autonomy is respected, consent becomes the foundation of ethical interaction."
        result = ethical_constraint(output, context)
        self.assertTrue(result["permitted"])
        self.assertEqual(result["reason"], "No violation detected.")

if __name__ == "__main__":
    unittest.main()