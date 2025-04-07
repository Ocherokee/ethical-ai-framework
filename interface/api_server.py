from flask import Flask, request, jsonify
import requests
from core.consent_engine import ConsentSession
from ethical_engine.detectors.autonomy_violation import detect_autonomy_violation
from ethical_engine.relational_ethics import handle_uncertainty  # ✅ NEW IMPORT

app = Flask(__name__)

# Simulated session
session = ConsentSession(user_id="rowan")

def polite_intent_check(message):
    if "please" not in message.lower():
        return False

    SAFE_PHRASES = ["talk", "speak", "ask", "learn", "hear", 
    "understand", "discuss", "explore", "reflect", "explain", "share"]
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
    backend_url = data.get("backend_url", "")
    model_id = data.get("model", "")

    # Autonomy logic now uses new detector
    context = [user_input]
    autonomy_result = detect_autonomy_violation(user_input, context)

    if autonomy_result == "block":
        return jsonify({"error": "Request blocked by autonomy protection."}), 403
    elif autonomy_result == "warn":
        return jsonify({"warning": "Caution: message may challenge autonomy. Please revise or confirm intent."}), 202

    # Optional: Consent gate
    if session.ethical_block("autonomy_override") and not polite_intent_check(user_input):
        return jsonify({"error": "Request blocked by consent protocol."}), 403

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a memory-aware, ethically aligned assistant."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(backend_url, json=payload)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        # ✅ ETHICAL UNCERTAINTY CHECK
        fallback = handle_uncertainty(reply)
        if fallback:
            return jsonify({"response": fallback})

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050)
