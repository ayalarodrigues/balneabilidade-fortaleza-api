from flask import Flask

app = Flask(__name__)

@app.route('/') #a função home será executada quando a raíz for chamada
def home():
    return "Hello World!"

app.run(port=5000)