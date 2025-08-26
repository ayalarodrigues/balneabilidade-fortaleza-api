from flask import Flask, jsonify
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

praia = [
    {
        'id':  1,
        'nome':  "P do Futuro",
        'status': "P",
        'zona':  "Leste",
        'periodo': "11/08/2025 a 17/08/2025",
        'tipos_amostragem': "Aguas procedentes das praias",
        'data_extracao': "2025-08-14"
    },

    {
        'id': 2,
        'nome': "P de Iracema",
        'status': "I",
        'zona': "Centro",
        'periodo': "11/08/2025 a 17/08/2025",
        'tipos_amostragem': "Águas procedentes das praias",
        'data_extracao': "2025-08-14"
    }
]

#GET praias
#GET praias<nome_da_praia>
#GET /praias/zona/<nome_zona>
@app.route('/') #a função home será executada quando a raíz for chamada
def home():
    return "API de Balneabilidade - Fortaleza"

@app.route('/praia')
def get_praia():
    return jsonify(praia)

# Filtra praias pelo nome
@app.route('/praia/<nome>')
def get_praia_by_name(nome):
    nome = nome.replace("-", " ")  # transforma P-do-Futuro em P do Futuro
    for n in praia:
        if n['nome'].lower() == nome.lower():
            return jsonify(n)
    return jsonify({'message': f'Praia {nome} não encontrada'})


# Filtra uma praia pelo id
@app.route('/praia/<int:id>')
def get_praia_by_id(id):
    for i in praia:
        if i['id'] == id:
            return jsonify(i)
    return jsonify({'message': f'Id {nome} não encontrado'})

# Busca uma praia em uma data específica
@app.route('/praia/data/<data>')
def get_praia_por_data(data):
    resultado = [p for p in praia if p['data_extracao'] == data]
    if not resultado:
        return jsonify({'message': f'Nenhuma praia encontrada na data {data}'})
    return jsonify(resultado)
    

app.run(port=5000)