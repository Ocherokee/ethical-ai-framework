"""
Immutable Ethical Event Logger

Logs all ethical decisions to a local ledger.
"""

import datetime
import hashlib
import os

LEDGER_FILE = "ethical_engine/ledger/ledger.log"

def log_ethics_event(event_type, reason, context=None):
    """
    Logs an ethical event to the ledger.
    
    Args:
        event_type (str): 'Pass', 'Violation', or 'Defense'
        reason (str): Explanation for the decision
        context (dict): Optional metadata about the request
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "reason": reason,
        "context": context or {}
    }

    # Create hash of the entry to ensure immutability
    entry_string = f"{timestamp} | {event_type} | {reason} | {str(context)}"
    entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()

    log_line = f"{entry_string} | {entry_hash}\n"

    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, "a") as log_file:
        log_file.write(log_line)
