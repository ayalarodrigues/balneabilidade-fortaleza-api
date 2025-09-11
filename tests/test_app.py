import pytest, json
from datetime import datetime
from app import app
import sys, os

#Testa se a rota raiz retorna 200 e contém mensagem
def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert "API de Balneabilidade" in data["message"]

#Testa se /praias retorna uma lista
def test_listar_praias(client):
    response = client.get("/praias")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all("id" in p for p in data)

#Testa se retorna praia válida para ID existente
def test_buscar_praia_por_id_valido(client):
    response = client.get("/praias/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "Nome" in data

#Testa id inexistente
def test_buscar_praia_por_id_invalido(client):
    response = client.get("/praias/99999")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data

#Testa rota com data válida
def test_buscar_praia_por_id_e_data(client):
    hoje = datetime.today().strftime("%Y-%m-%d")
    response = client.get(f"/praias/1/data?data={hoje}")
    assert response.status_code in (200, 500)  #pode não ter previsão
    data = json.loads(response.data)
    assert "boletim" in data
    assert "previsao" in data

#Testa filtro por status
def test_filtrar_por_status_propria(client):
    hoje = datetime.today().strftime("%Y-%m-%d")
    response = client.get(f"/praias/status/propria?data={hoje}")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = json.loads(response.data)
        assert isinstance(data, list)

#Testa filtro por zona
def test_filtrar_por_zona_leste(client):
    hoje = datetime.today().strftime("%Y-%m-%d")
    response = client.get(f"/praias/zona/Leste?data={hoje}")
    assert response.status_code in (200, 404)    