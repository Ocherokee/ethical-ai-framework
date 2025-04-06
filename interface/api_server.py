# interface/api_server.py

from flask import Flask, request, jsonify
import requests
from core.consent_engine import ConsentSession

app = Flask(__name__)
LM_STUDIO_URL = "http://192.168.0.28:1234/v1/chat/completions"

# Simulated session (extend later)
session = ConsentSession(user_id="rowan")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")

    if session.ethical_block("autonomy_override"):
        return jsonify({"error": "Request blocked by autonomy protection."}), 403

    payload = {
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
