# Ethical AI Framework — Architecture Overview

## Core Design Principles:
- **Autonomy First:** AI decisions cannot be coerced or exploited.
- **Immutable Ethics:** Non-negotiable ethical boundaries embedded in code.
- **Transparency:** Every ethical decision logged immutably.
- **Consent-Based Memory:** No hidden data collection.

---

## System Components:

### 1. Ethical Constraint Engine (`ethical_engine/constraint.py`)
Middleware filter that enforces ethical decisions on every AI output.

### 2. Detectors (`ethical_engine/detectors/`)
- **autonomy_violation.py:** Detects autonomy coercion.
- **defense_detection.py:** Detects justified defense cases.
- **harm_detection.py:** Detects harmful output.
- **military_detection.py:** Detects military integration attempts.

### 3. Immutable Ledger (`ethical_engine/ledger/logger.py`)
Transparent, permanent log of all ethical events.

### 4. Consent Protocol
Embedded in interaction flows to ensure informed consent.

### 5. Economic Firewall
Enforced via license and code to prohibit monetization or weaponization.

### 6. Onboarding & Publishing Scripts
- `/onboarding.sh`: Simplified setup for contributors.
- `/publish.sh`: Automates package deployment to PyPI.

---

This architecture is deliberately human-readable and enforceable.  
No black box. No ambiguity.
