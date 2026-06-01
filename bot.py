import os, json, datetime, re, urllib.request, urllib.parse
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

memoria = []

def buscar_wikipedia(termo):
    try:
        q = urllib.parse.quote(termo)
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{q}"
        req = urllib.request.Request(url, headers={"User-Agent":"BotVoz/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read())
            return d.get("extract","")[:300]
    except:
        return ""

def responder(msg):
    msg_lower = msg.lower().strip()
    hora = datetime.datetime.now().strftime("%H:%M")
    data = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # Saudações
    if any(p in msg_lower for p in ["oi","olá","ola","bom dia","boa tarde","boa noite","hey","e aí","eai"]):
        h = int(datetime.datetime.now().strftime("%H"))
        period = "bom dia" if h<12 else "boa tarde" if h<18 else "boa noite"
        return f"{period}! Estou aqui e pronto para conversar. Como posso te ajudar?"

    # Hora e data
    if any(p in msg_lower for p in ["que horas","hora","horas"]):
        return f"Agora são {hora}."
    if any(p in msg_lower for p in ["que dia","data","hoje é"]):
        return f"Hoje é {data}."

    # Sobre o bot
    if any(p in msg_lower for p in ["quem é você","seu nome","como se chama","o que você é"]):
        return "Sou o BotVoz, sua IA assistente pessoal! Fui criado para conversar com você a qualquer hora, por voz ou texto."
    if any(p in msg_lower for p in ["como você está","tudo bem","tudo bom"]):
        return "Estou ótimo e pronto para te ajudar! E você, como está?"
    if "obrigado" in msg_lower or "obrigada" in msg_lower or "valeu" in msg_lower:
        return "De nada! Estou sempre aqui quando precisar."
    if any(p in msg_lower for p in ["tchau","até logo","até mais","bye"]):
        return "Até logo! Foi um prazer conversar com você. Volte quando quiser!"

    # Matemática
    if any(p in msg_lower for p in ["quanto é","calcule","calcula","resultado de"]):
        expr = re.sub(r'[^0-9+\-*/().,\s]','', msg_lower)
        expr = expr.replace(',','.')
        try:
            r = eval(expr)
            return f"O resultado é {r}."
        except:
            pass

    # Piadas
    if any(p in msg_lower for p in ["piada","me conta uma piada","me faça rir"]):
        piadas = [
            "Por que o livro de matemática ficou triste? Porque tinha muitos problemas!",
            "O que o zero disse para o oito? Bonito cinto!",
            "Por que o computador foi ao médico? Porque estava com vírus!",
            "Qual é o animal mais antigo? A zebra, porque é preto e branco!"
        ]
        import random
        return random.choice(piadas)

    # Motivação
    if any(p in msg_lower for p in ["motivação","me anime","me encoraje","estou triste","desanimado"]):
        return "Você é capaz de realizar coisas incríveis! Cada dia é uma nova oportunidade. Continue firme, o sucesso está no caminho!"

    # Perguntas gerais - busca Wikipedia
    if any(p in msg_lower for p in ["o que é","quem foi","quem é","me fale sobre","me conta sobre","explique","como funciona"]):
        # Extrai o termo de busca
        for prefix in ["o que é","quem foi","quem é","me fale sobre","me conta sobre","explique","como funciona"]:
            if prefix in msg_lower:
                termo = msg_lower.replace(prefix,"").strip()
                if termo:
                    info = buscar_wikipedia(termo)
                    if info:
                        return f"Sobre {termo}: {info}"
                break
        return f"É uma ótima pergunta sobre '{msg}'! Posso buscar mais informações se você me der mais detalhes."

    # Clima/tempo
    if any(p in msg_lower for p in ["clima","tempo","vai chover","temperatura"]):
        return "Não tenho acesso ao clima em tempo real, mas você pode verificar no Google ou no app de clima do seu celular!"

    # Notícias
    if any(p in msg_lower for p in ["notícia","novidade","o que aconteceu"]):
        return "Para notícias em tempo real, recomendo acessar o G1, UOL ou BBC Brasil. Posso ajudar com outra coisa?"

    # Conselhos
    if any(p in msg_lower for p in ["conselho","me aconselhe","o que devo fazer","me ajuda"]):
        return "Claro! Me conta mais sobre a situação para eu poder te ajudar melhor."

    # Memória
    if len(memoria) > 0 and any(p in msg_lower for p in ["o que eu disse","lembra","lembras"]):
        ultima = memoria[-1]["pergunta"] if memoria else ""
        return f"A última coisa que você me disse foi: '{ultima}'"

    # Resposta genérica inteligente
    respostas = [
        f"Entendi! Você disse: '{msg}'. Me conta mais sobre isso.",
        f"Que assunto interessante! Pode elaborar mais sobre '{msg}'?",
        f"Estou processando o que você disse. O que exatamente você quer saber sobre isso?",
        f"Boa pergunta! Você pode me dar mais detalhes sobre '{msg}'?",
    ]
    import random
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
    memoria.append({"pergunta":msg,"resposta":resposta})
    if len(memoria) > 50:
        memoria.pop(0)
    
    return jsonify({"resposta":resposta,"precisa_autorizacao":False})

@app.route("/status")
def status():
    return jsonify({"status":"online","interacoes":len(memoria)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
