from flask import Flask, jsonify, Response, request
import json
from datetime import datetime
import pandas as pd
import subprocess
import os
import sys
import requests

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #para suportar acentos

# --- Rodar scraper.py automaticamente antes de carregar os dados ---
SCRAPER_FILE = "scraper.py"
if os.path.exists(SCRAPER_FILE):
    print("Executando scraper para atualizar boletim...")
    subprocess.run([sys.executable, SCRAPER_FILE], check=True)
else:
    print("Arquivo scraper.py não encontrado. Continuando com o CSV existente.")

# --- Função para sempre retornar JSON com acentos ---
def json_response(data, status=200):
    return Response(json.dumps(data, ensure_ascii=False), status=status, mimetype="application/json")


# --- Carregar os dados gerados pelo scraper ---
CSV_FILE = "boletim_fortaleza.csv"
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    raise FileNotFoundError(f"O arquivo {CSV_FILE} não foi encontrado. Execute o scraper primeiro.")

#converter o df para lista de dicionário
praias = df.to_dict(orient="records")
df = pd.read_csv(CSV_FILE, encoding='utf-8')


# --- Função para obter previsão do tempo e marinha ---
def get_forecast(lat, lon, data, hora=None):
    """
    Retorna previsão meteorológica e marinha para a latitude/longitude fornecida
    na data e hora desejadas.
    
    Unidades:
        - temperatura: °C
        - sensação térmica: °C
        - velocidade do vento: km/h
        - direção do vento: graus
        - chuva: mm
        - cobertura de nuvens: %
        - altura das ondas: metros
        - direção das ondas: graus
        - período das ondas: segundos
    """
    hora_consulta = hora if hora else "12:00"  # padrão meio-dia

    # URLs das APIs Open-Meteo
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,apparent_temperature,"
        "windspeed_10m,winddirection_10m,precipitation,cloudcover"
        f"&start_date={data}&end_date={data}&timezone=America/Fortaleza"
    )

    marine_url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}&hourly=wave_height,wave_direction,wave_period"
        f"&start_date={data}&end_date={data}&timezone=America/Fortaleza"
    )

    # Requisições
    weather_response = requests.get(weather_url)
    marine_response = requests.get(marine_url)

    weather_data = weather_response.json() if weather_response.status_code == 200 else {}
    marine_data = marine_response.json() if marine_response.status_code == 200 else {}

    # Estrutura padrão do retorno
    forecast = {
        "data": data,
        "hora_consulta": hora_consulta,
        "temperatura_c": None,
        "sensacao_termica_c": None,
        "velocidade_vento_kmh": None,
        "direcao_vento_graus": None,
        "chuva_mm": None,
        "cobertura_nuvens_pct": None,
        "altura_ondas_m": None,
        "direcao_ondas_graus": None,
        "periodo_ondas_s": None
    }

    # Extrair índice da hora desejada
    if "hourly" in weather_data:
        times = weather_data["hourly"]["time"]
        alvo = f"{data}T{hora_consulta}"
        if alvo not in times:
            hora_proxima = min(times, key=lambda h: abs(datetime.fromisoformat(h) - datetime.fromisoformat(alvo)))
        else:
            hora_proxima = alvo
        idx = times.index(hora_proxima)
        forecast.update({
            "temperatura_c": weather_data["hourly"]["temperature_2m"][idx],
            "sensacao_termica_c": weather_data["hourly"]["apparent_temperature"][idx],
            "velocidade_vento_kmh": weather_data["hourly"]["windspeed_10m"][idx],
            "direcao_vento_graus": weather_data["hourly"]["winddirection_10m"][idx],
            "chuva_mm": weather_data["hourly"]["precipitation"][idx],
            "cobertura_nuvens_pct": weather_data["hourly"]["cloudcover"][idx]
        })

    if "hourly" in marine_data:
        times = marine_data["hourly"]["time"]
        alvo = f"{data}T{hora_consulta}"
        if alvo not in times:
            hora_proxima = min(times, key=lambda h: abs(datetime.fromisoformat(h) - datetime.fromisoformat(alvo)))
        else:
            hora_proxima = alvo
        idx = times.index(hora_proxima)
        forecast.update({
            "altura_ondas_m": marine_data["hourly"]["wave_height"][idx],
            "direcao_ondas_graus": marine_data["hourly"]["wave_direction"][idx],
            "periodo_ondas_s": marine_data["hourly"]["wave_period"][idx]
        })

    return forecast


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

    return json_response(praias_resumo)
 
#buscar praia pelo id
@app.route("/praias/<int:id>")
def buscar_praia_por_id(id):
    praia = next((p for p in praias if p["id"] == id), None)
    if not praia:
        return json_response({"message": f"Nenhuma praia encontrada com id {id}"}), 404
   
    return json_response(praia)

#buscar informações das praias pelo id e data
@app.route("/praias/<int:id>/data")
def buscar_praia_por_id_e_data(id):
    #query param: ?data=YYYY-MM-DD
    data = request.args.get("data")
    praia = next((p for p in praias if p["id"] == id), None)
    if not praia:
        return json_response({"message": f"Nenhuma praia encontrada com id {id}"}), 404

    if data and data not in str(praia["Dias_Periodo"]).split(", "):
        return json_response({"message": f"A praia com id {id} não possui boletim para {data}"}), 404

    return json_response(praia)

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
        return json_response({"message": "Status inválido. Use 'propria' ou 'impropria'."}), 400

    resultado = [p for p in praias if p["Status"] == status_filtrado]

    if data:
        resultado = [p for p in resultado if data in str(p["Dias_Periodo"]).split(", ")]

    if not resultado:
        return json_response({"message": f"Nenhuma praia encontrada com status {status_filtrado}"}), 404

    return json_response(resultado)


#buscar praias por zona geográfica (Leste, Centro, Oeste) e data opcional (?data=YYYY-MM-DD)
@app.route("/praias/zona/<zona>")
def filtrar_por_zona(zona):
    data = request.args.get("data")
    zona_filtrada = zona.capitalize()

    resultado = [p for p in praias if p["Zona"] == zona_filtrada]

    if data:
        resultado = [p for p in resultado if data in str(p["Dias_Periodo"]).split(", ")]

    if not resultado:
        return json_response({"message": f"Nenhuma praia encontrada na zona {zona_filtrada}"}), 404

    return json_response(resultado)



if __name__ == "__main__":
    lat, lon = -3.7227, -38.4793  # Praia do Futuro
    dados = get_forecast(lat, lon, "2025-09-10", "14:00")
    print(json.dumps(dados, indent=4, ensure_ascii=False))
    app.run(port=5000)