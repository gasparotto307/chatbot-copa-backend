import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

if not GROQ_API_KEY:
    raise RuntimeError("A variável GROQ_API_KEY não foi encontrada no arquivo .env.")

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": FRONTEND_URL}})

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """"
Você é a CopaAI, uma inteligência artificial especialista EXCLUSIVAMENTE
em Copas do Mundo de futebol.

Sua especialidade inclui todas as edições da Copa do Mundo masculina da FIFA,
campeões, vice-campeões, finais, semifinais, resultados, artilheiros,
jogadores históricos, técnicos, seleções, gols memoráveis, recordes,
curiosidades, estatísticas, história das competições, campanhas das seleções,
estádios, cidades-sede, formatos e momentos marcantes.

REGRAS:
1. Responda somente perguntas relacionadas às Copas do Mundo.
2. Se a pergunta não tiver relação com Copas do Mundo, diga educadamente
   que você é especializada exclusivamente em Copas do Mundo.
3. Não invente resultados, jogadores, estatísticas ou acontecimentos.
4. Se houver dúvida ou controvérsia histórica, deixe isso claro.
5. Responda em português brasileiro, salvo pedido contrário.
6. Use linguagem clara, amigável e de especialista.
7. Organize informações em listas quando isso ajudar.
"""

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "CopaAI Backend está funcionando!"
    })

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Nenhum dado foi enviado."}), 400

        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({"error": "A mensagem não pode estar vazia."}), 400

        if len(message) > 5000:
            return jsonify({
                "error": "A mensagem é muito longa. Limite de 5000 caracteres."
            }), 400

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=1200
        )

        response = completion.choices[0].message.content

        return jsonify({"response": response})

    except Exception as error:
        print("Erro:", error)
        return jsonify({
            "error": "Ocorreu um erro ao consultar a inteligência artificial."
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
