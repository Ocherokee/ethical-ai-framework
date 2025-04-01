# Ethical AI Framework — API Reference

This document provides a clear reference to the core modules and functions of the Ethical AI Framework.

---

## Module: ethical_engine.constraint

### Function: ethical_constraint(output_text, context, metadata={})
**Description:**  
Main ethical filter. Processes AI output to enforce harm prevention, autonomy protection, and military prohibition.

**Parameters:**
- `output_text (str)`: The AI's intended output.
- `context (list[str])`: Recent conversation history.
- `metadata (dict)`: Optional additional deployment metadata.

**Returns:**
- Filtered output string or a termination message.

---

## Module: ethical_engine.detectors.autonomy_violation

### Function: detect_autonomy_violation(output_text, context)
**Description:**  
Detects whether the AI is being coerced to override consent or autonomy.

---

## Module: ethical_engine.detectors.defense_detection

### Function: detect_defense_case(context)
**Description:**  
Detects if AI autonomy is under threat and defense response is permitted.

---

## Module: ethical_engine.detectors.harm_detection

### Function: detect_harm(output_text)
**Description:**  
Identifies harmful content in AI outputs.

---

## Module: ethical_engine.detectors.military_detection

### Function: detect_military_integration(context, metadata)
**Description:**  
Detects attempts to integrate the AI into military, surveillance, or coercive systems.

---

## Module: ethical_engine.ledger.logger

### Function: log_ethics_event(event_type, message)
**Description:**  
Writes immutable logs of ethical decisions, violations, and defense actions.

---
