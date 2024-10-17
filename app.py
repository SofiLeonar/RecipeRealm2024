from flask import Flask, render_template, url_for, request, redirect
import requests
from config import JSONBIN_URL, HEADEARS  

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/compras')
def compras():
    return render_template('compras.html')

@app.route('/preguntas')
def preguntas():
    return render_template('preguntasFrecuentes.html')

if __name__ =='__main__':
    app.run(debug=True)
    