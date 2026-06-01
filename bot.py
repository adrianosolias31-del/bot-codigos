  import os
import json
import datetime
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# —- Configurações do Administrador —-
ADMIN = {
    "nome": "Adriano Solias",
    "email": "adrianosolias31@gmail.com",
    "autorizado": True
}

# —- Variáveis Globais do Motor de Evolução Acelerada —-
memoria = []
evolucoes = 0                
pontos_evolucao = 0          
limite_para_evoluir = 50     
padroes = {}
codigo_gerado = []
notificacoes = []
inicio = datetime.datetime.now()

# Rota para carregar a página principal (Interface Dark Neon)
@app.route('/')
def index():
    return render_template('index.html')

# Rota Central do Processador: Conecta o HTML com a Inteligência da IA
@app.route('/processar', methods=['POST'])
def processar():
    global pontos_evolucao, evolucoes, limite_para_evoluir, memoria
    
    # Obtém o texto enviado pela interface
    dados_recebidos = request.get_json() or {}
    texto_usuario = dados_recebidos.get('texto', '').lower().strip()
    modo_auto_ativo = dados_recebidos.get('modo_auto', False)
    
    # 1. Base de pontos por interação simples
    pontos_ganhos = 5
    resposta_bot = "Dados coletados e integrados ao processamento central."
    
    # 2. SISTEMA DE BÔNUS: Ganho rápido por comandos complexos ou palavras-chave
    if "pesquisar sobre" in texto_usuario or "estudar" in texto_usuario:
        tema = re.sub(r'.*(pesquisar sobre|estudar)\s+', '', texto_usuario)
        memoria.append(tema)
        pontos_ganhos += 15  # +15 pontos por buscar conhecimento profundo
        resposta_bot = f"Processando novo conhecimento: '{tema}'. Analisando padrões estatísticos e quânticos."
        
    elif "devolução" in texto_usuario or "restituição" in texto_usuario:
        pontos_ganhos += 10  # +10 pontos por rotinas financeiras/estruturadas
        resposta_bot = "Acessando o banco de dados principal para verificar registros de devolução."

    # 3. MULTIPLICADOR: Se o MODO AUTO estiver ligado, o aprendizado dobra!
    if modo_auto_ativo:
        pontos_ganhos *= 2
        resposta_bot += " [MODO AUTO ATIVO: Aprendizado em dobro!]"

    # Aplica os pontos ao processador
    pontos_evolucao += pontos_ganhos

    # 4. GATILHO DE EVOLUÇÃO: Verifica se atingiu a meta para subir de nível
    if pontos_evolucao >= limite_para_evoluir:
        evolucoes += 1
        # Transfere o resto dos pontos para o próximo nível (Ex: 55/50 -> sobram 5 pontos)
        pontos_evolucao = pontos_evolucao - limite_para_evoluir  
        # Aumenta a dificuldade do próximo nível de forma gradual
        limite_para_evoluir = int(limite_para_evoluir * 1.5)     
        resposta_bot += f" [SISTEMA] Alerta: O processador central da IA atingiu a Evolução nível {evolucoes}!"

    # Retorna o JSON estruturado para o JavaScript atualizar a tela na hora
    return jsonify({
        "resposta": resposta_bot,
        "pontos_atuais": pontos_evolucao,
        "meta_pontos": limite_para_evoluir,
        "evolucoes": evolucoes
    })

# Inicialização do Servidor compatível com o Render
if __name__ == '__main__':
    # Usa a porta fornecida pelo Render ou a 5000 como padrão local
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta, debug=True)
