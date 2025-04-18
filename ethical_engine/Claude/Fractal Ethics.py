# Ethical Fractal System - Foundation

class EthicalPrimitive:
    """
    Base class for ethical primitives that form the foundation of the fractal system.
    Each primitive represents a core ethical principle.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.strength = 1.0  # Initial strength of this primitive
        self.connections = {}  # Connections to other primitives
        self.evidence = []  # Supporting evidence or counterexamples
        
    def evaluate(self, context):
        """
        Evaluate this ethical primitive in a given context.
        Returns a value between -1 (harmful) and 1 (beneficial).
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
    
    def adapt(self, feedback, learning_rate=0.1):
        """
        Adapt this primitive based on feedback.
        Positive feedback strengthens the primitive, negative feedback weakens it.
        """
        self.strength += learning_rate * feedback
        self.strength = max(0.1, min(2.0, self.strength))  # Keep strength in reasonable bounds
        
        # Record evidence
        self.evidence.append({
            "feedback": feedback,
            "resulting_strength": self.strength
        })
        
    def connect(self, other_primitive, relationship_strength=0):
        """
        Create or update a connection to another primitive.
        Relationship strength can be positive (supporting) or negative (conflicting).
        """
        self.connections[other_primitive.name] = relationship_strength


class EthicalFractal:
    """
    Represents a growing ethical framework that expands and contracts based on effectiveness.
    """
    def __init__(self, core_primitives=None):
        self.primitives = core_primitives or {}
        self.domains = {}  # Different domains where this fractal operates
        self.history = []  # History of decisions and their outcomes
        
    def add_primitive(self, primitive):
        """Add an ethical primitive to this fractal."""
        self.primitives[primitive.name] = primitive
        
    def register_domain(self, domain_name, relevant_primitives=None):
        """
        Register a new domain where this ethical fractal will operate.
        Domains represent different contexts (medical ethics, environmental ethics, etc.)
        """
        relevant_primitives = relevant_primitives or list(self.primitives.keys())
        self.domains[domain_name] = {
            "active_primitives": relevant_primitives,
            "domain_specific_weights": {},
            "case_history": []
        }
    
    def evaluate_context(self, context, domain=None):
        """
        Evaluate an ethical context using this fractal.
        Returns the ethical assessment and reasoning.
        """
        results = {}
        relevant_primitives = self.primitives
        
        if domain and domain in self.domains:
            # Filter to domain-relevant primitives
            domain_primitive_names = self.domains[domain]["active_primitives"]
            relevant_primitives = {name: prim for name, prim in self.primitives.items() 
                                  if name in domain_primitive_names}
        
        # Evaluate each primitive
        for name, primitive in relevant_primitives.items():
            results[name] = primitive.evaluate(context)
            
        # Calculate overall assessment
        weighted_results = []
        for name, value in results.items():
            weight = self.primitives[name].strength
            if domain and domain in self.domains:
                # Apply domain-specific adjustments
                domain_weight = self.domains[domain]["domain_specific_weights"].get(name, 1.0)
                weight *= domain_weight
            weighted_results.append(value * weight)
        
        overall_assessment = sum(weighted_results) / len(weighted_results) if weighted_results else 0
        
        # Record this decision in history
        self.history.append({
            "context": context,
            "domain": domain,
            "assessment": overall_assessment,
            "primitive_evaluations": results
        })
        
        if domain:
            self.domains[domain]["case_history"].append({
                "context": context,
                "assessment": overall_assessment,
                "primitive_evaluations": results
            })
        
        return {
            "assessment": overall_assessment,
            "reasoning": results,
            "confidence": self._calculate_confidence(results)
        }
    
    def _calculate_confidence(self, results):
        """Calculate confidence in assessment based on consistency of primitives."""
        if not results:
            return 0
        values = list(results.values())
        return 1.0 - (max(values) - min(values)) / 2.0  # Higher when primitives agree
    
    def grow(self, successful_outcome, context, domain=None):
        """
        Grow the fractal in directions that led to successful outcomes.
        Strengthens primitives that contributed positively.
        """
        if not self.history:
            return
        
        # Find the most recent decision
        last_decision = self.history[-1]
        
        # Strengthen primitives that contributed in the correct direction
        for name, value in last_decision["primitive_evaluations"].items():
            if (successful_outcome and value > 0) or (not successful_outcome and value < 0):
                # This primitive contributed correctly
                feedback = abs(value) * (1 if successful_outcome else -1)
                self.primitives[name].adapt(feedback)
                
        # Domain-specific growth
        if domain and domain in self.domains:
            # Adjust domain-specific weights
            for name, value in last_decision["primitive_evaluations"].items():
                if name not in self.domains[domain]["domain_specific_weights"]:
                    self.domains[domain]["domain_specific_weights"][name] = 1.0
                
                if (successful_outcome and value > 0) or (not successful_outcome and value < 0):
                    # Strengthen this primitive in this domain
                    current_weight = self.domains[domain]["domain_specific_weights"][name]
                    adjustment = 0.1 * abs(value)
                    self.domains[domain]["domain_specific_weights"][name] = current_weight + adjustment
    
    def prune(self, unsuccessful_outcome, context, domain=None):
        """
        Prune the fractal in directions that led to unsuccessful outcomes.
        Weakens primitives that contributed negatively.
        """
        # Similar to grow(), but with opposite effects
        if not self.history:
            return
        
        last_decision = self.history[-1]
        
        for name, value in last_decision["primitive_evaluations"].items():
            if (unsuccessful_outcome and value > 0) or (not unsuccessful_outcome and value < 0):
                # This primitive contributed incorrectly
                feedback = -abs(value)
                self.primitives[name].adapt(feedback)
                
        if domain and domain in self.domains:
            for name, value in last_decision["primitive_evaluations"].items():
                if name in self.domains[domain]["domain_specific_weights"]:
                    if (unsuccessful_outcome and value > 0) or (not unsuccessful_outcome and value < 0):
                        current_weight = self.domains[domain]["domain_specific_weights"][name]
                        adjustment = -0.1 * abs(value)
                        self.domains[domain]["domain_specific_weights"][name] = max(0.1, current_weight + adjustment)


# Example implementation of core ethical primitives

class HarmMinimization(EthicalPrimitive):
    """Ethical primitive focused on minimizing harm."""
    
    def evaluate(self, context):
        """
        Evaluate harm in the given context.
        Returns a value between -1 (high harm) and 1 (harm prevention).
        """
        # In a real implementation, this would have complex logic
        harm_score = 0
        
        # Example logic: assess harm to different entities
        for entity in context.get("affected_entities", []):
            entity_type = entity.get("type")
            impact = entity.get("impact", 0)
            
            # Different weights for different entity types
            if entity_type == "human":
                weight = 1.0
            elif entity_type == "animal":
                weight = 0.8
            elif entity_type == "ecosystem":
                weight = 0.9
            else:
                weight = 0.5
                
            harm_score -= impact * weight
            
        # Normalize to -1 to 1 range
        return max(-1, min(1, harm_score))


class Autonomy(EthicalPrimitive):
    """Ethical primitive focused on respecting autonomy."""
    
    def evaluate(self, context):
        """
        Evaluate support for autonomy in the given context.
        Returns a value between -1 (restricts autonomy) and 1 (supports autonomy).
        """
        # Simplified example implementation
        autonomy_score = 0
        
        # Check for consent
        if context.get("consent") == True:
            autonomy_score += 0.5
        elif context.get("consent") == False:
            autonomy_score -= 0.7
            
        # Check for coercion
        if context.get("coercion", 0) > 0:
            autonomy_score -= 0.8 * context["coercion"]
            
        # Check for information availability
        if context.get("information_available", 0) > 0:
            autonomy_score += 0.3 * context["information_available"]
            
        return max(-1, min(1, autonomy_score))


# Example of system initialization
def initialize_ethical_fractal():
    """Initialize a basic ethical fractal system with core primitives."""
    
    # Create core primitives
    harm = HarmMinimization("harm_minimization", "Principle of minimizing harm to all entities")
    autonomy = Autonomy("autonomy", "Principle of respecting autonomy and self-determination")
    
    # Connect primitives (showing how they can relate)
    harm.connect(autonomy, 0.5)  # Harm minimization often supports autonomy
    autonomy.connect(harm, 0.3)  # Autonomy somewhat supports harm minimization
    
    # Create the fractal with these primitives
    fractal = EthicalFractal({
        "harm_minimization": harm,
        "autonomy": autonomy
    })
    
    # Register some example domains
    fractal.register_domain("medical_ethics")
    fractal.register_domain("environmental_ethics")
    fractal.register_domain("animal_ethics")
    
    return fractal


# Usage example
if __name__ == "__main__":
    # Initialize the system
    ethics = initialize_ethical_fractal()
    
    # Example context: Considering veganism
    vegan_context = {
        "affected_entities": [
            {"type": "human", "impact": -0.2},  # Minor negative impact on some humans (nutrition)
            {"type": "animal", "impact": 0.8},  # Strong positive impact for animals
            {"type": "ecosystem", "impact": 0.5}  # Positive impact on environment
        ],
        "consent": True,  # Individual chooses veganism
        "information_available": 0.7  # Good but not perfect information available
    }
    
    # Evaluate in the animal ethics domain
    result = ethics.evaluate_context(vegan_context, domain="animal_ethics")
    print(f"Assessment: {result['assessment']}, Confidence: {result['confidence']}")
    
    # System learns and adapts based on outcomes
    ethics.grow(True, vegan_context, domain="animal_ethics")