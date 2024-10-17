from flask import Flask, render_template, url_for, request, redirect, jsonify
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

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Faltan datos'}), 400

    email = data.get('email') 
    password = data.get('password')  


    if not email or not password:
        return jsonify({'error': 'Faltan datos'}), 400

    try:
        response = requests.get(JSONBIN_URL, headers=HEADEARS)
        if response.status_code != 200:
            return jsonify({'error': 'Error al acceder a los datos'}), 500

        users = response.json().get('record', [])
        
        for user in users:
            if user.get('email') == email and user.get('password') == password:
                return jsonify({'message': 'Login correcto'}), 200

        return jsonify({'error': 'Credenciales incorrectas'}), 401

    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/registrarse', methods=['POST'])
def registrarse():
    email = request.form('email')
    password = request.form('password')

    if not email or not password:
        return jsonify({'error': 'Faltan datos'}), 400

    response = requests.get(JSONBIN_URL, headers=HEADEARS)
    users = response.json().get('record', [])

    for user in users:
        if user.get('email') == email:
            return jsonify({'error': 'El usuario ya existe'}), 400

    nuevo_usuario = {
        'email': email,
        'password': password
    }

    users.append(nuevo_usuario)

    response = requests.put(
        JSONBIN_URL, json=users)
    if response.status_code == 200:
        return jsonify({'message': 'Usuario creado correctamente'}), 200
    else:
        return jsonify({'error': 'Error al registrar el usuario'}), 500

    
if __name__ =='__main__':
    app.run(debug=True)
    