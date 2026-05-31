import os
from flask import Flask,request,jsonify
import requests
app=Flask(__name__)
K=os.environ.get('GROQ_KEY','')
U='https://api.groq.com/openai/v1/chat/completions'
M='meta-llama/llama-4-scout-17b-16e-instruct'
@app.route('/perguntar',methods=['POST'])
def perguntar():
 p=request.json.get('pedido','')
 h={'Authorization':f'Bearer {K}','Content-Type':'application/json'}
 b={'model':M,'messages':[{'role':'user','content':p}]}
 r=requests.post(U,headers=h,json=b)
 return jsonify({'resposta':r.json()['choices'][0]['message']['content']})
@app.route('/')
def home():
 return 'Bot funcionando!'
if __name__=='__main__':
 app.run(host='0.0.0.0',port=10000)
