from flask import Flask, jsonify, Response, request
import json
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #para suportar acentos

# --- Carregar os dados gerados pelo scraper ---
CSV_FILE = "boletim_fortaleza.csv"
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    raise FileNotFoundError(f"O arquivo {CSV_FILE} não foi encontrado. Execute o scraper primeiro.")

#converter o df para lista de dicionário
praias = df.to_dict(orient="records")
df = pd.read_csv(CSV_FILE, encoding='utf-8')




# --- Rotas ---

#rota raiz
@app.route('/') #a função home será executada quando a raíz for chamada
def home():
    data = {
        "message": "API de Balneabilidade - Fortaleza",
        "info": (
            "Cada praia tem um identificador numérico único (id). "
            "Use o endpoint /praias para listar todos os ids e nomes, "
            "e consulte informações detalhadas usando o id."
        ),
        "example": {
            "listagem": "/praias",
            "busca_por_id": "/praias/5",
            "busca_por_id_com_data": "/praias/5/data?data=2025-09-01",
            "busca_por_status": "/praias/status/propria?data=2025-09-01",
            "busca_por_zona": "/praias/zona/Leste?data=2025-09-01"
        }
    }
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype='application/json') #correção de acentos
    # - ensure_ascii=False: mantém os caracteres acentuados legíveis
    # - indent=4: deixa o JSON formatado, mais fácil de ler
    #retorna um Response com mimetype 'application/json'

#rota para listar todas as praias
@app.route("/praias")
def listar_praias():
    praias_resumo = [
        {"id": p["id"], "nome": p["Nome"], "zona": p["Zona"]}
        for p in praias
    ]
    #isso aqui é apenas para corrigir o problema dos acentos gráficos
    return Response(
    json.dumps(praias_resumo, ensure_ascii=False),
    mimetype='application/json'
)

#buscar praia pelo id
@app.route("/praias/<int:id>")
def buscar_praia_por_id(id):
    praia = next((p for p in praias if p["id"] == id), None)
    if not praia:
        return jsonify({"message": f"Nenhuma praia encontrada com id {id}"}), 404
    return jsonify(praia)

#buscar informações das praias pelo id e data
@app.route("/praias/<int:id>/data")
def buscar_praia_por_id_e_data(id):
    #query param: ?data=YYYY-MM-DD
    data = request.args.get("data")
    praia = next((p for p in praias if p["id"] == id), None)
    if not praia:
        return jsonify({"message": f"Nenhuma praia encontrada com id {id}"}), 404

    if data and data not in str(praia["Dias_Periodo"]).split(", "):
        return jsonify({"message": f"A praia com id {id} não possui boletim para {data}"}), 404

    return jsonify(praia)

#buscar praia por status com data opcional
@app.route("/praias/status/<status>")
def filtrar_por_status(status):
    data = request.args.get("data")
    status_map = {
        "propria": "Própria para banho",
        "impropria": "Imprópria para banho"
    }
    status_filtrado = status_map.get(status.lower())
    if not status_filtrado:
        return jsonify({"message": "Status inválido. Use 'propria' ou 'impropria'."}), 400

    resultado = [p for p in praias if p["Status"] == status_filtrado]

    if data:
        resultado = [p for p in resultado if data in str(p["Dias_Periodo"]).split(", ")]

    if not resultado:
        return jsonify({"message": f"Nenhuma praia encontrada com status {status_filtrado}"}), 404

    return jsonify(resultado)



app.run(port=5000)