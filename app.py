from flask import Flask, jsonify, Response, request
import json
from datetime import datetime
import pandas as pd
import subprocess
import os
import sys
import requests
from coordenadas import COORDENADAS_POR_CODIGO

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

    # Extrair índice da hora desejada (meteorologia)
    if "hourly" in weather_data:
        times = weather_data["hourly"]["time"]
        alvo = f"{data}T{hora_consulta}"
        if alvo in times:
            idx = times.index(alvo)
            forecast.update({
                "temperatura_c": weather_data["hourly"]["temperature_2m"][idx],
                "sensacao_termica_c": weather_data["hourly"]["apparent_temperature"][idx],
                "velocidade_vento_kmh": weather_data["hourly"]["windspeed_10m"][idx],
                "direcao_vento_graus": weather_data["hourly"]["winddirection_10m"][idx],
                "chuva_mm": weather_data["hourly"]["precipitation"][idx],
                "cobertura_nuvens_pct": weather_data["hourly"]["cloudcover"][idx]
            })

    # Extrair índice da hora desejada (marinha)
    if "hourly" in marine_data:
        times = marine_data["hourly"]["time"]
        alvo = f"{data}T{hora_consulta}"
        if alvo in times:
            idx = times.index(alvo)
            forecast.update({
                "altura_ondas_m": marine_data["hourly"]["wave_height"][idx],
                "direcao_ondas_graus": marine_data["hourly"]["wave_direction"][idx],
                "periodo_ondas_s": marine_data["hourly"]["wave_period"][idx]
            })

    # Se todos os dados estiverem None, significa que a previsão não está disponível
    if all(value is None for key, value in forecast.items() if key not in ["data", "hora_consulta"]):
        forecast = {
            "mensagem": f"Previsão meteorológica e marinha não disponível para {data} e hora {hora_consulta}",
            "data": data,
            "hora_consulta": hora_consulta
        }

    return forecast


# --- Função para extrair código da praia ---
def extrair_codigo(praia):
    # Caso exista campo 'Codigo', usa ele; senão extrai do Nome (ex: "05L - P. do Futuro")
    if "Codigo" in praia and praia["Codigo"]:
        return praia["Codigo"]
    return praia["Nome"].split(" ")[0]  # ex: "05L"

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
#buscar informações das praias pelo id e data
@app.route("/praias/<int:id>/data")
def buscar_praia_por_id_e_data(id):
    #query params: ?data=YYYY-MM-DD&hora=HH:MM 
    data = request.args.get("data")
    hora = request.args.get("hora", "12:00")  # padrão meio-dia

    if not data:
        return json_response({"message": "É necessário informar a data no formato YYYY-MM-DD"}, 400)

    praia = next((p for p in praias if p["id"] == id), None)
    if not praia:
        return json_response({"message": f"Nenhuma praia encontrada com id {id}"}), 404

    # Extrai código da praia
    codigo = praia.get("Codigo") or praia["Nome"].split(" ")[0]  # ex: "05L"
    if not codigo or codigo not in COORDENADAS_POR_CODIGO:
        return json_response({"message": "Coordenadas da praia não disponíveis"}, 500)

    lat_str, lon_str = COORDENADAS_POR_CODIGO[codigo].split(", ")
    lat, lon = float(lat_str), float(lon_str)

    #obter previsão meteorológica e marinha
    forecast = get_forecast(lat, lon, data, hora)

    #checar boletim Semace
    boletim_disponivel = data in str(praia["Dias_Periodo"]).split(", ")
    boletim = praia if boletim_disponivel else f"Não há boletim da Semace disponível para {data}"

    resposta = {
        "boletim": boletim,
        "previsao": forecast
    }

    return json_response(resposta)


#buscar praia por status com data opcional e previsão meteorológica
@app.route("/praias/status/<status>")
def filtrar_por_status(status):
    """
    Filtra praias por status (propria/impropria).
    - Se 'data' for informada, tenta incluir 'previsao' (Open-Meteo).
    - Se 'data' não for informada, não inclui 'previsao' para evitar retornos com null.
    """
    data = request.args.get("data")
    hora = request.args.get("hora", "12:00")

    status_map = {
        "propria": "Própria para banho",
        "impropria": "Imprópria para banho"
    }
    status_filtrado = status_map.get(status.lower())
    if not status_filtrado:
        return json_response({"message": "Status inválido. Use 'propria' ou 'impropria'."}), 400

    # Filtra pelas praias que têm o status solicitado
    resultado = [p for p in praias if p["Status"] == status_filtrado]

    # Se data for passada, filtra também por boletim daquela data
    if data:
        resultado = [p for p in resultado if data in str(p["Dias_Periodo"]).split(", ")]

    # Sem resultados e sem data => 404
    if not resultado and not data:
        return json_response({"message": f"Nenhuma praia encontrada com status {status_filtrado}"}), 404

    resposta = []
    for praia in resultado:
        # Se não passou data: não buscamos previsão (evita previsao:null)
        if not data:
            resposta.append({
                "praia": praia,
                "info": "Para obter previsão, informe ?data=YYYY-MM-DD&hora=HH:MM (hora opcional)."
            })
            continue

        # A partir daqui sabemos que data foi informada -> tentar previsão
        codigo = extrair_codigo(praia)
        if codigo and codigo in COORDENADAS_POR_CODIGO:
            lat_str, lon_str = COORDENADAS_POR_CODIGO[codigo].split(", ")
            lat, lon = float(lat_str), float(lon_str)

            # Chama a API de previsão (get_forecast já trata caso sem dados)
            forecast = get_forecast(lat, lon, data, hora)
        else:
            # Se não houver coordenadas, informamos isso em 'previsao'
            forecast = {"mensagem": "Coordenadas não disponíveis"}

        boletim_disponivel = data in str(praia["Dias_Periodo"]).split(", ")

        # Se nem boletim nem previsão => mensagem clara
        if not boletim_disponivel and (not forecast or "mensagem" in forecast):
            resposta.append({
                "praia": praia["Nome"],
                "mensagem": f"Não há dados disponíveis para {data}"
            })
        else:
            resposta.append({
                "praia": praia,
                "previsao": forecast
            })

    return json_response(resposta)

#buscar praias por zona geográfica e data opcional com previsão meteorológica
@app.route("/praias/zona/<zona>")
def filtrar_por_zona(zona):
    """
    Filtra praias por zona. Comportamento similar a /praias/status:
    - Se 'data' for informada, inclui 'previsao' quando possível.
    - Se 'data' não for informada, não inclui 'previsao' (evita null).
    """
    data = request.args.get("data")
    hora = request.args.get("hora", "12:00")

    zona_filtrada = zona.capitalize()
    resultado = [p for p in praias if p["Zona"] == zona_filtrada]

    # Se data for passada, filtra por boletins dessa data
    if data:
        resultado = [p for p in resultado if data in str(p["Dias_Periodo"]).split(", ")]

    # Sem resultados e sem data => 404
    if not resultado and not data:
        return json_response({"message": f"Nenhuma praia encontrada na zona {zona_filtrada}"}), 404

    resposta = []
    for praia in resultado:
        # Sem data: não buscamos previsão, apenas fornecemos instrução
        if not data:
            resposta.append({
                "praia": praia,
                "info": "Para obter previsão, informe ?data=YYYY-MM-DD&hora=HH:MM (hora opcional)."
            })
            continue

        # Com data: tenta obter previsão via coordenadas
        codigo = extrair_codigo(praia)
        if codigo and codigo in COORDENADAS_POR_CODIGO:
            lat_str, lon_str = COORDENADAS_POR_CODIGO[codigo].split(", ")
            lat, lon = float(lat_str), float(lon_str)

            forecast = get_forecast(lat, lon, data, hora)
        else:
            forecast = {"mensagem": "Coordenadas não disponíveis"}

        boletim_disponivel = data in str(praia["Dias_Periodo"]).split(", ")

        if not boletim_disponivel and (not forecast or "mensagem" in forecast):
            resposta.append({
                "praia": praia["Nome"],
                "mensagem": f"Não há dados disponíveis para {data}"
            })
        else:
            resposta.append({
                "praia": praia,
                "previsao": forecast
            })

    return json_response(resposta)



if __name__ == "__main__":
    lat, lon = -3.7227, -38.4793  # Praia do Futuro
    dados = get_forecast(lat, lon, "2025-09-10", "14:00")
    print(json.dumps(dados, indent=4, ensure_ascii=False))
    app.run(port=5000)