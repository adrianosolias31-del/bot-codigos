import os
from flask import Flask, request, jsonify
import urllib.request
import json

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

@app.route("/")
def home():
    return "Bot funcionando!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("mensagem", "")
    if not GROQ_API_KEY:
        return jsonify({"resposta": "Configure GROQ_API_KEY!", "precisa_autorizacao": False})
    payload = json.dumps({
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Responda em portugues de forma natural."},
            {"role": "user", "content": msg}
        ],
        "max_tokens": 300
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resposta = json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        resposta = f"Erro: {str(e)}"
    return jsonify({"resposta": resposta, "precisa_autorizacao": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
