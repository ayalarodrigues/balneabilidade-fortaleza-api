from flask import Flask, jsonify
import json
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #para suportar acentos

df = pd.read_csv("boletim_fortaleza.csv")
df["Dias_Periodo"] = df["Dias_Periodo"].str.split(", ")  # transforma string em lista


@app.route('/') #a função home será executada quando a raíz for chamada
def home():
    return "API de Balneabilidade - Fortaleza"    

app.run(port=5000)