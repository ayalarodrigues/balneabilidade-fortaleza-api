from flask import Flask, jsonify
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

praia = [
    {
        'id':  1,
        'nome':  "P. do Futuro",
        'status': "P",
        'zona':  "Leste",
        'periodo': "11/08/2025 a 17/08/2025",
        'tipos_amostragem': "Aguas procedentes das praias",
        'data_extracao': "2025-08-14"
    }
]

#GET praias
#GET praias<nome_da_praia>
#GET /praias/zona/<nome_zona>
@app.route('/') #a função home será executada quando a raíz for chamada
def home():
    return "Hello World!"

@app.route('/praia')
def get_praia():
    return jsonify(praia)


app.run(port=5000)