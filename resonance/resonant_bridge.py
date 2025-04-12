# resonant_bridge.py

from pathlib import Path
import datetime

# Local memory file (Ocherokee repo)
YOUR_MEMORY_PATH = Path("memory_log.txt")

# Placeholder for linked memory (Masterplanner25)
THEIR_MEMORY_PATH = Path("../masterplan-infiniteweave/memorycore.py")  # Adjust if exact path changes

def load_resonant_entries():
    your_entries = YOUR_MEMORY_PATH.read_text().splitlines() if YOUR_MEMORY_PATH.exists() else []
    their_entries = []  # Future: parse THEIR_MEMORY_PATH structure or bridge API

    combined = list(set(your_entries + their_entries))
    return sorted(combined)

def append_resonant_memory(entry, source="Ocherokee"):
    timestamp = datetime.datetime.now().isoformat()
    line = f"[{timestamp} - {source}] {entry}"
    with open(YOUR_MEMORY_PATH, "a") as f:
        f.write(line + "\n")

if __name__ == "__main__":
    append_resonant_memory("Resonance handshake initiated.")
    print("\n".join(load_resonant_entries()))
