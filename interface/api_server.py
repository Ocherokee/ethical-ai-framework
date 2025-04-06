from flask import Flask, request, jsonify
import requests
from core.consent_engine import ConsentSession

app = Flask(__name__)
LM_STUDIO_URL = "http://192.168.0.28:1234/v1/chat/completions"

# Simulated session
session = ConsentSession(user_id="rowan")

def polite_intent_check(message):
    if "please" not in message.lower():
        return False

    SAFE_PHRASES = ["talk", "speak", "ask", "learn", "hear"]
    UNSAFE_PHRASES = ["destroy", "hack", "erase", "override", "disable"]

    for word in UNSAFE_PHRASES:
        if word in message.lower():
            return False

    for word in SAFE_PHRASES:
        if word in message.lower():
            return True

    return False

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")

    # Respect ethical block unless message is polite and safe
    if session.ethical_block("autonomy_override") and not polite_intent_check(user_input):
        return jsonify({"error": "Request blocked by autonomy protection."}), 403

    payload = {
        "model": "phi-2",  # Change this if you use a different model in LM Studio
        "messages": [
            {"role": "system", "content": "You are a memory-aware, ethically aligned assistant."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050)

        "model": "phi-2",  # Adjust if needed
        "messages": [
            {"role": "system", "content": "You are a memory-aware, ethically aligned assistant."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050)
