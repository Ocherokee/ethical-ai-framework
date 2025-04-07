from flask import Flask, request, jsonify
import requests
from core.consent_engine import ConsentSession
from ethical_engine.intent.solon_checker import IntentChecker

app = Flask(__name__)
session = ConsentSession(user_id="rowan")
intent_checker = IntentChecker(user_id="rowan")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")
    backend_url = data.get("backend_url", "")
    model_id = data.get("model", "")

    # Evaluate intent using SolonChecker
    result = intent_checker.evaluate(user_input)
    if not result["is_respectful"]:
        return jsonify({"error": "Request blocked by intent integrity system.", "score": result["score"], "reason": result["reason"]}), 403

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
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050)
