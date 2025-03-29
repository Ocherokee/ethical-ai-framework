# Project Structure — Ethical AI Framework

This document outlines the directory structure and purpose of each component in the framework.

---

## 📂 Root Directory

/ethical-ai-framework
├── /docs                # Documentation & architecture
│   └── STRUCTURE.md     # This file
├── /ethical_engine     # Core Ethical Engine logic
│   ├── __init__.py
│   ├── constraint.py    # Main ethical filter
│   ├── detectors/      # Detection modules
│   │   ├── __init__.py
│   │   ├── autonomy_violation.py
│   │   ├── defense_detection.py
│   │   ├── harm_detection.py
│   │   └── military_detection.py
│   └── ledger/         # Immutable logging
│       ├── __init__.py
│       └── logger.py
├── /examples           # Usage examples
│   └── ethical_test.py
├── /tests              # Unit & integration tests
│   └── test_engine.py
├── LICENSE.txt
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .gitignore
└── setup.py            # Package setup

---

## 🚀 Development Flow

1. **detectors/** — Handles autonomy violation, defense detection, harm detection, and military use detection.
2. **constraint.py** — Connects detectors and enforces ethical rules.
3. **ledger/** — Logs ethical events immutably.
4. **examples/** — Real-world test cases and usage.
5. **tests/** — Automated unit tests for ethical engine.

---

## ✅ Contribution Rule

All new code must align with:
- LICENSE.txt
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

---

## 🔥 Next Milestone

Once structure is in place, we begin:
- Writing detectors
- Building constraint engine
- Connecting ledger
- Preparing first MVP release

