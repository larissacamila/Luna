import json
import random
from flask import Flask, request, jsonify, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
# CARREGAR INTENTS
# =========================
with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

patterns = []
tags = []
responses = {}

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(pattern.lower())
        tags.append(intent["tag"])
    responses[intent["tag"]] = intent["responses"]

# =========================
# VETORIZAÇÃO
# =========================
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(patterns)

# =========================
# CORE DA LUNA
# =========================
def get_response(user_input: str) -> str:
    if not user_input.strip():
        return "🌙 Pode repetir? Não consegui entender."

    user_input = user_input.lower()
    user_vec = vectorizer.transform([user_input])

    similarities = cosine_similarity(user_vec, X)
    best_match = similarities.argmax()
    confidence = similarities[0][best_match]

    fallbacks = [
        "🌙 Não entendi muito bem sua pergunta. Pode explicar melhor?",
        "🌙 Acho que perdi alguma coisa 😅 pode reformular?",
        "🌙 Me conta com outras palavras?",
        "🌙 Não tenho certeza do que você quis dizer."
    ]

    if confidence < 0.3:
        return random.choice(fallbacks)

    tag = tags[best_match]
    return random.choice(responses[tag])

# =========================
# API CHAT (PADRÃO)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    texto = data.get("texto", "").strip()

    resposta = get_response(texto)

    return jsonify({
        "response": resposta
    })

# =========================
# TESTE RÁPIDO NO BROWSER
# =========================
@app.route("/test")
def test():
    msg = request.args.get("msg", "")
    resposta = get_response(msg)
    return f"<h2>Luna:</h2><p>{resposta}</p>"

# =========================
# SERVIR HTML (OPCIONAL)
# =========================
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
