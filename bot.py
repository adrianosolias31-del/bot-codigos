 import os
import json
import datetime
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

ADMIN = {
    "nome": "Adriano Solias",
    "email": "adrianosolias31@gmail.com",
    "autorizado": True
}

memoria = []
evolucoes = 0                
pontos_evolucao = 0          
limite_para_evoluir = 50     
padroes = {}
codigo_gerado = []
notificacoes = []
inicio = datetime.datetime.now()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    global pontos_evolucao, evolucoes, limite_para_evoluir, memoria
    
    dados_recebidos = request.get_json() or {}
    texto_usuario = dados_recebidos.get('texto', '').lower().strip()
    modo_auto_ativo = dados_recebidos.get('modo_auto', False)
    
    pontos_ganhos = 5
    resposta_bot = "Dados coletados e integrados ao processamento central."
    
    if "pesquisar sobre" in texto_usuario or "estudar" in texto_usuario:
        tema = re.sub(r'.*(pesquisar sobre|estudar)\s+', '', texto_usuario)
        memoria.append(tema)
        pontos_ganhos += 15  
        resposta_bot = f"Processando novo conhecimento: '{tema}'. Analisando padrões estatísticos."
        
    elif "devolução" in texto_usuario or "restituição" in texto_usuario:
        pontos_ganhos += 10  
        resposta_bot = "Acessando o banco de dados principal para verificar registros."

    if modo_auto_ativo:
        pontos_ganhos *= 2
        resposta_bot += " [MODO AUTO ATIVO: Aprendizado em dobro!]"

    pontos_evolucao += pontos_ganhos

    if pontos_evolucao >= limite_para_evoluir:
        evolucoes += 1
        pontos_evolucao = pontos_evolucao - limite_para_evoluir  
        limite_para_evoluir = int(limite_para_evoluir * 1.5)     
        resposta_bot += f" [SISTEMA] Alerta: O processador atingiu a Evolução nível {evolucoes}!"

    return jsonify({
        "resposta": resposta_bot,
        "pontos_atuais": pontos_evolucao,
        "meta_pontos": limite_para_evoluir,
        "evolucoes": evolucoes
    })

if __name__ == '__main__':
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
 
