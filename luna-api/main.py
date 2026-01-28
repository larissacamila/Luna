from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import urllib.parse

# ===== CONFIGURAÇÕES =====
PASTA_CONHECIMENTO = "conhecimento"
NAO_RESPONDIDAS = "nao_respondidas.txt"

# ===== CARREGAR BASE =====
def carregar_base():
    base = []
    if not os.path.exists(PASTA_CONHECIMENTO):
        os.makedirs(PASTA_CONHECIMENTO)

    for arquivo in os.listdir(PASTA_CONHECIMENTO):
        if arquivo.endswith(".txt"):
            caminho = os.path.join(PASTA_CONHECIMENTO, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        base.append(linha)
    return base

BASE = carregar_base()

# ===== HANDLER HTTP =====
class LunaHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/perguntar"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            pergunta = params.get("q", [""])[0]

            resposta = self.responder(pergunta)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps({
                "pergunta": pergunta,
                "resposta": resposta
            }, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def responder(self, pergunta):
        pergunta = pergunta.lower().strip()
        palavras = pergunta.split()

        for linha in BASE:
            score = sum(1 for p in palavras if p in linha.lower())
            if score >= 2:
                return linha

        # Salva perguntas não respondidas
        try:
            with open(NAO_RESPONDIDAS, "a", encoding="utf-8") as f:
                f.write(pergunta + "\n")
        except:
            pass

        return "Ainda não tenho essa resposta. Posso consultar e te responder depois."

    # Evita logs poluídos no Render
    def log_message(self, format, *args):
        return

# ===== INICIAR SERVIDOR =====
def iniciar():
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8000))

    server = HTTPServer((host, port), LunaHandler)
    print(f"🌙 Luna API rodando em http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    iniciar()
