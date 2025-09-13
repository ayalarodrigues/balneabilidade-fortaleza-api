import sys, os
import pytest
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.app import app

# --- Fixture ---

#cliente teste do flask usado para simular requisições HTTP sem precisar "rodar" o servidor
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

# --- Mock ---

#"mocka" todas as chamadas requests.get usadas dentro do app.py
#evita chamadas externas reais para a api Open-Meteo e site da SEMA
@pytest.fixture(autouse=True)
def mock_requests_get(mocker):
    hoje = datetime.today().strftime("%Y-%m-%d")
    hora = "12:00"
    alvo = f"{hoje}T{hora}"

    #mock para previsão do temp
    mock_weather = mocker.Mock()
    mock_weather.status_code = 200
    mock_weather.json.return_value = {
        "hourly": {
            "time": [alvo],
            "temperature_2m": [28],
            "apparent_temperature": [30],
            "windspeed_10m": [15],
            "winddirection_10m": [120],
            "precipitation": [0],
            "cloudcover": [20],
        }
    }

    #mock para previsão marinha
    mock_marine = mocker.Mock()
    mock_marine.status_code = 200
    mock_marine.json.return_value = {
        "hourly": {
            "time": [alvo],
            "wave_height": [1.2],
            "wave_direction": [180],
            "wave_period": [6.5],
        }
    }

    #patch: toda vez que requests.get for chamado, decide qual mock usar
    def fake_requests_get(url, *args, **kwargs):
        if "marine-api.open-meteo.com" in url:
            return mock_marine
        return mock_weather

    mocker.patch("requests.get", side_effect=fake_requests_get)
    return mock_weather
