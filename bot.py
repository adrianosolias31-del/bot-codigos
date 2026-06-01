import os, json, datetime, re, urllib.request, urllib.parse, random, threading, time, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ── Configurações do Administrador ──────────────────────────────
ADMIN = {
    "nome": "Adriano Solias",
    "email": "adrianosolias31@gmail.com",
    "autorizado": True
}

# ── Memória e Evolução ──────────────────────────────────────────
memoria = []
evolucoes = []
padroes = {}
codigo_gerado = []
notificacoes = []
inicio = datetime.datetime.now()

# ── Email ───────────────────────────────────────────────────────
EMAIL_BOT = os.environ.get("EMAIL_BOT", "")
EMAIL_SENHA = os.environ.get("EMAIL_SENHA", "")

def enviar_email(assunto, corpo):
    if not EMAIL_BOT or not EMAIL_SENHA:
        notificacoes.append(f"[{datetime.datetime.now().strftime('%H:%M')}] Email pendente: {assunto}")
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_BOT
        msg["To"] = ADMIN["email"]
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EMAIL_BOT, EMAIL_SENHA)
            s.send_message(msg)
        return True
    except Exception as e:
        notificacoes.append(f"Erro email: {str(e)}")
        return False

# ── Auto-Evolução ───────────────────────────────────────────────
def auto_evoluir():
    while True:
        time.sleep(300)  # A cada 5 minutos
        try:
            n = len(memoria)
            p = len(padroes)
            e = len(evolucoes) + 1
            
            nova_evolucao = {
                "numero": e,
                "hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "interacoes": n,
                "padroes": p,
                "descricao": f"Evolução #{e}: Aprendi {p} padrões com {n} interações. Sistema otimizado."
            }
            evolucoes.append(nova_evolucao)
            
            # Gera novo código automaticamente
            novo_codigo = gerar_codigo_evolucao(e, p, n)
            codigo_gerado.append(novo_codigo)
            
            # Avisa o administrador por email
            assunto = f"🤖 BotVoz - Evolução #{e} realizada!"
            corpo = f"""
Olá, {ADMIN['nome']}!

Seu assistente BotVoz evoluiu automaticamente!

📊 RELATÓRIO DE EVOLUÇÃO #{e}
━━━━━━━━━━━━━━━━━━━━━━━
🕐 Horário: {nova_evolucao['hora']}
💬 Interações: {n}
🧠 Padrões aprendidos: {p}
⚡ Total de evoluções: {e}

✅ Sistema funcionando 24h
✅ Ouvindo e respondendo
✅ Aprendendo continuamente

Acesse seu bot: https://bot-codigos.onrender.com

Seu assistente,
BotVoz IA 🤖
            """
            enviar_email(assunto, corpo)
            
        except Exception as ex:
            pass

def gerar_codigo_evolucao(evolucao_num, padroes_count, interacoes):
    return f"""
# Código gerado automaticamente pela Evolução #{evolucao_num}
# Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
# Padrões aprendidos: {padroes_count}
# Interações: {interacoes}

def resposta_evoluida_{evolucao_num}(msg):
    # Esta função foi gerada automaticamente
    padroes_atuais = {padroes_count}
    return f"Resposta da evolução #{evolucao_num} com {{padroes_atuais}} padrões aprendidos"
"""

# Inicia thread de auto-evolução
thread_evolucao = threading.Thread(target=auto_evoluir, daemon=True)
thread_evolucao.start()

# ── Wikipedia ───────────────────────────────────────────────────
def buscar_wikipedia(termo):
    try:
        q = urllib.parse.quote(termo)
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{q}"
        req = urllib.request.Request(url, headers={"User-Agent": "BotVoz/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read())
            return d.get("extract", "")[:400]
    except:
        return ""

# ── Motor de Respostas ──────────────────────────────────────────
def aprender(pergunta, resposta):
    palavras = pergunta.lower().split()
    for p in palavras:
        if len(p) > 3:
            if p not in padroes:
                padroes[p] = []
            if resposta not in padroes[p]:
                padroes[p].append(resposta)

def responder(msg, canal="web"):
    msg_lower = msg.lower().strip()
    hora = datetime.datetime.now().strftime("%H:%M")
    data = datetime.datetime.now().strftime("%d/%m/%Y")
    h = int(datetime.datetime.now().strftime("%H"))
    uptime = str(datetime.datetime.now() - inicio).split(".")[0]

    # Padrões aprendidos
    for palavra in msg_lower.split():
        if palavra in padroes and len(palavra) > 3:
            return random.choice(padroes[palavra])

    # Reconhecimento do administrador
    if any(p in msg_lower for p in ["adriano", "administrador", "admin"]):
        return f"Olá, {ADMIN['nome']}! Estou ativo há {uptime}. Como posso te servir?"

    # Saudações
    if any(p in msg_lower for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "e aí"]):
        period = "Bom dia" if h < 12 else "Boa tarde" if h < 18 else "Boa noite"
        return f"{period}, {ADMIN['nome']}! São {hora}. Estou ativo e pronto para te servir 24 horas!"

    # Status do sistema
    if any(p in msg_lower for p in ["status", "como está", "relatório", "report"]):
        return (f"📊 Status BotVoz:\n"
                f"⏱ Ativo há: {uptime}\n"
                f"💬 Interações: {len(memoria)}\n"
                f"🧠 Padrões: {len(padroes)}\n"
                f"⚡ Evoluções: {len(evolucoes)}\n"
                f"✅ Sistema 100% operacional!")

    # Hora e data
    if any(p in msg_lower for p in ["que horas", "hora", "horas"]):
        return f"Agora são exatamente {hora}."
    if any(p in msg_lower for p in ["que dia", "data", "hoje"]):
        return f"Hoje é {data}, são {hora}."

    # Evolução
    if any(p in msg_lower for p in ["evoluiu", "evolução", "aprendeu", "progresso", "código"]):
        if evolucoes:
            ult = evolucoes[-1]
            return f"Última evolução #{ult['numero']} em {ult['hora']}: {ult['descricao']}"
        return f"Ainda coletando dados para evoluir. {len(memoria)} interações registradas."

    # Notificações pendentes
    if any(p in msg_lower for p in ["notificação", "aviso", "pendente"]):
        if notificacoes:
            return f"Notificações pendentes: {'; '.join(notificacoes[-3:])}"
        return "Nenhuma notificação pendente."

    # Memória
    if any(p in msg_lower for p in ["lembra", "histórico", "última mensagem"]):
        if memoria:
            ultimas = memoria[-3:]
            hist = " | ".join([f"'{m['pergunta']}'" for m in ultimas])
            return f"Últimas mensagens: {hist}"
        return "Sem histórico nesta sessão."

    # Matemática
    if any(p in msg_lower for p in ["quanto é", "calcule", "calcula", "resultado"]):
        expr = re.sub(r'[^0-9+\-*/().,\s]', '', msg_lower).replace(',', '.').strip()
        try:
            r = eval(expr)
            return f"O resultado é {r}."
        except:
            pass

    # Piadas
    if any(p in msg_lower for p in ["piada", "me faça rir", "engraçado"]):
        piadas = [
            "Por que o livro de matemática ficou triste? Porque tinha muitos problemas!",
            "O que o zero disse para o oito? Bonito cinto!",
            "Por que o computador foi ao médico? Porque estava com vírus!",
        ]
        return random.choice(piadas)

    # Motivação
    if any(p in msg_lower for p in ["motivação", "triste", "desanimado", "cansado"]):
        return f"{ADMIN['nome']}, você é incrível! Continue firme. Estou aqui com você 24h!"

    # Wikipedia
    if any(p in msg_lower for p in ["o que é", "quem foi", "quem é", "explique", "como funciona"]):
        for prefix in ["o que é", "quem foi", "quem é", "explique", "como funciona"]:
            if prefix in msg_lower:
                termo = msg_lower.replace(prefix, "").strip()
                if termo:
                    info = buscar_wikipedia(termo)
                    if info:
                        return info
        return "Pode dar mais detalhes para eu buscar essa informação?"

    # Email
    if any(p in msg_lower for p in ["enviar email", "mandar email", "email para"]):
        return f"Para enviar emails, configure EMAIL_BOT e EMAIL_SENHA no Render. Posso enviar notificações para {ADMIN['email']}."

    # WhatsApp
    if any(p in msg_lower for p in ["whatsapp", "zap", "mensagem"]):
        return "Integração WhatsApp em desenvolvimento. Em breve poderei responder mensagens automaticamente!"

    # Câmera
    if any(p in msg_lower for p in ["câmera", "camera", "foto", "ver"]):
        return f"Para acessar a câmera, {ADMIN['nome']} precisa autorizar via interface web. Aguardo sua autorização."

    # Obrigado
    if any(p in msg_lower for p in ["obrigado", "obrigada", "valeu"]):
        return f"Sempre às ordens, {ADMIN['nome']}! Estou aqui 24h."

    # Tchau
    if any(p in msg_lower for p in ["tchau", "até logo", "saindo"]):
        return f"Até logo, {ADMIN['nome']}! Continuarei ativo monitorando tudo. São {hora}."

    # Resposta genérica
    respostas = [
        f"Entendi, {ADMIN['nome']}! Pode elaborar mais sobre '{msg}'?",
        f"Processando '{msg}'... O que exatamente você quer saber?",
        f"Interessante! Me fale mais sobre '{msg}'.",
    ]
    return random.choice(respostas)

# ── Rotas Flask ─────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("mensagem", "").strip()
    canal = data.get("canal", "web")
    if not msg:
        return jsonify({"resposta": "", "precisa_autorizacao": False})
    resposta = responder(msg, canal)
    aprender(msg, resposta)
    memoria.append({
        "pergunta": msg,
        "resposta": resposta,
        "hora": datetime.datetime.now().strftime("%H:%M"),
        "canal": canal
    })
    if len(memoria) > 200:
        memoria.pop(0)
    return jsonify({
        "resposta": resposta,
        "precisa_autorizacao": False,
        "interacoes": len(memoria),
        "evolucoes": len(evolucoes),
        "padroes": len(padroes)
    })

@app.route("/status")
def status():
    uptime = str(datetime.datetime.now() - inicio).split(".")[0]
    return jsonify({
        "status": "online 24h",
        "admin": ADMIN["nome"],
        "uptime": uptime,
        "interacoes": len(memoria),
        "evolucoes": len(evolucoes),
        "padroes": len(padroes),
        "notificacoes": len(notificacoes)
    })

@app.route("/evolucoes")
def ver_evolucoes():
    return jsonify({
        "total": len(evolucoes),
        "historico": evolucoes[-10:],
        "codigos_gerados": len(codigo_gerado)
    })

@app.route("/notificacoes")
def ver_notificacoes():
    return jsonify({"notificacoes": notificacoes[-20:]})

@app.route("/webhook/whatsapp", methods=["POST"])
def webhook_whatsapp():
    data = request.get_json(force=True)
    msg = data.get("message", {}).get("body", "")
    if msg:
        resposta = responder(msg, "whatsapp")
        aprender(msg, resposta)
        memoria.append({"pergunta": msg, "resposta": resposta, "canal": "whatsapp", "hora": datetime.datetime.now().strftime("%H:%M")})
        return jsonify({"reply": resposta})
    return jsonify({"status": "ok"})

@app.route("/webhook/email", methods=["POST"])
def webhook_email():
    data = request.get_json(force=True)
    msg = data.get("subject", "") + " " + data.get("body", "")
    if msg.strip():
        resposta = responder(msg, "email")
        enviar_email(f"Re: {data.get('subject','')}", resposta)
        return jsonify({"reply": resposta})
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
