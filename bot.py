import os
from flask import Flask, request, jsonify, render_template
import urllib.request
import json
import time

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("mensagem", "")
    if not GEMINI_API_KEY:
        return jsonify({"resposta": "Configure GEMINI_API_KEY!", "precisa_autorizacao": False})
    
    modelos = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-pro"]
    
    for modelo in modelos:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": f"Responda em português natural e curto: {msg}"}]}]
            }).encode()
            req = urllib.request.Request(url, data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                result = json.loads(r.read())
                resposta = result["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"resposta": resposta, "precisa_autorizacao": False})
        except Exception as e:
            if "429" not in str(e):
                return jsonify({"resposta": f"Erro: {str(e)}", "precisa_autorizacao": False})
            time.sleep(2)
            continue
    
    return jsonify({"resposta": "Limite atingido. Tente em 1 minuto.", "precisa_autorizacao": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
