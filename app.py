from flask import Flask, jsonify, Response
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







app.run(port=5000)