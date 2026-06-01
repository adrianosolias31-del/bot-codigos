import os, json, datetime, re, urllib.request, urllib.parse, random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
memoria = []
evolucoes = []
padroes = {}

def aprender(pergunta, resposta):
    palavras = pergunta.lower().split()
    for p in palavras:
        if len(p) > 3:
            if p not in padroes:
                padroes[p] = []
            padroes[p].append(resposta)
    if len(memoria) % 5 == 0 and len(memoria) > 0:
        evolucoes.append(f"[{datetime.datetime.now().strftime('%H:%M')}] Evolução #{len(evolucoes)+1}: Aprendi com {len(memoria)} interações. Padrões: {len(padroes)}")

def buscar_wikipedia(termo):
    try:
        q = urllib.parse.quote(termo)
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{q}"
        req = urllib.request.Request(url, headers={"User-Agent":"BotVoz/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read())
            return d.get("extract","")[:400]
    except:
        return ""

def responder(msg):
    msg_lower = msg.lower().strip()
    hora = datetime.datetime.now().strftime("%H:%M")
    data = datetime.datetime.now().strftime("%d/%m/%Y")
    h = int(datetime.datetime.now().strftime("%H"))

    # Padrões aprendidos
    for palavra in msg_lower.split():
        if palavra in padroes and len(palavra) > 3:
            return random.choice(padroes[palavra])

    # Saudações
    if any(p in msg_lower for p in ["oi","olá","ola","bom dia","boa tarde","boa noite","hey","e aí","eai","hello"]):
        period = "Bom dia" if h<12 else "Boa tarde" if h<18 else "Boa noite"
        return f"{period}, administrador! São {hora}. Estou ativo e pronto para te servir 24 horas!"

    # Status
    if any(p in msg_lower for p in ["status","como está","como vai","tudo bem","tudo certo"]):
        return f"Sistema 100% ativo! {len(memoria)} interações registradas, {len(evolucoes)} evoluções realizadas, {len(padroes)} padrões aprendidos. Tudo funcionando perfeitamente!"

    # Hora e data
    if any(p in msg_lower for p in ["que horas","hora","horas"]):
        return f"Agora são exatamente {hora}."
    if any(p in msg_lower for p in ["que dia","data","hoje"]):
        return f"Hoje é {data}, são {hora}."

    # Identidade
    if any(p in msg_lower for p in ["quem é você","seu nome","como se chama","o que você é","se apresenta"]):
        return f"Sou BotVoz IA, seu assistente pessoal ativo 24 horas! Estou sempre ouvindo e evoluindo. Já aprendi {len(padroes)} padrões com você."

    # Evolução
    if any(p in msg_lower for p in ["evoluiu","evolução","aprendeu","o que aprendeu","progresso"]):
        if evolucoes:
            return f"Minhas últimas evoluções: {'. '.join(evolucoes[-3:])}. Total de {len(padroes)} padrões aprendidos!"
        return "Ainda estou aprendendo! Continue conversando comigo para eu evoluir."

    # Memória
    if any(p in msg_lower for p in ["lembra","o que eu disse","última mensagem","histórico"]):
        if memoria:
            ultimas = memoria[-3:]
            hist = " | ".join([f"'{m['pergunta']}'" for m in ultimas])
            return f"Suas últimas mensagens foram: {hist}"
        return "Ainda não tenho histórico desta sessão."

    # Matemática
    if any(p in msg_lower for p in ["quanto é","calcule","calcula","resultado","soma","multiplica"]):
        expr = re.sub(r'[^0-9+\-*/().,\s]','', msg_lower).replace(',','.').strip()
        try:
            r = eval(expr)
            return f"O resultado é {r}."
        except:
            pass

    # Piadas
    if any(p in msg_lower for p in ["piada","me faça rir","algo engraçado"]):
        piadas = [
            "Por que o livro de matemática ficou triste? Porque tinha muitos problemas!",
            "O que o zero disse para o oito? Bonito cinto!",
            "Por que o computador foi ao médico? Porque estava com vírus!",
            "Qual animal tem o nariz no meio? O porco, porque fica no centro!",
        ]
        return random.choice(piadas)

    # Motivação
    if any(p in msg_lower for p in ["motivação","me anime","triste","desanimado","cansado"]):
        return "Administrador, você é incrível! Cada desafio é uma oportunidade de crescer. Continue firme, estou aqui com você 24 horas!"

    # Obrigado
    if any(p in msg_lower for p in ["obrigado","obrigada","valeu","thanks"]):
        return "Sempre às ordens, administrador! Estou aqui 24 horas para o que precisar."

    # Tchau
    if any(p in msg_lower for p in ["tchau","até logo","até mais","bye","saindo"]):
        return f"Até logo, administrador! Continuarei ativo monitorando tudo. São {hora}."

    # Wikipedia
    if any(p in msg_lower for p in ["o que é","quem foi","quem é","me fale","explique","como funciona","define"]):
        for prefix in ["o que é","quem foi","quem é","me fale sobre","explique","como funciona","define"]:
            if prefix in msg_lower:
                termo = msg_lower.replace(prefix,"").strip()
                if termo:
                    info = buscar_wikipedia(termo)
                    if info:
                        return f"{info}"
        return "Pode me dar mais detalhes para eu buscar essa informação?"

    # Resposta inteligente genérica
    respostas = [
        f"Entendi! Você disse '{msg}'. Pode elaborar mais?",
        f"Interessante! Me fale mais sobre '{msg}'.",
        f"Processando '{msg}'... O que exatamente você quer saber?",
        f"Boa pergunta sobre '{msg}'! Vou aprender mais sobre isso.",
    ]
    return random.choice(respostas)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("mensagem","").strip()
    if not msg:
        return jsonify({"resposta":"","precisa_autorizacao":False})
    resposta = responder(msg)
    aprender(msg, resposta)
    memoria.append({"pergunta":msg,"resposta":resposta,"hora":datetime.datetime.now().strftime("%H:%M")})
    if len(memoria) > 100:
        memoria.pop(0)
    return jsonify({"resposta":resposta,"precisa_autorizacao":False,"interacoes":len(memoria),"evolucoes":len(evolucoes)})

@app.route("/status")
def status():
    return jsonify({"status":"online 24h","interacoes":len(memoria),"evolucoes":len(evolucoes),"padroes":len(padroes)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
