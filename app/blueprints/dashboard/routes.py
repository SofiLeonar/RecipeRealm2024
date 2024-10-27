from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint, jsonify
import requests
from . import dashboard_bp
from app.blueprints.auth.routes import cargar_users_jsonbin
from config import JSONBIN_URL, HEADERS

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
def home():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/nosotros')
def nosotros():
    return render_template('dashboard/nosotros.html')

@dashboard_bp.route('/compras')
def compras():
    return render_template('dashboard/compras.html')

@dashboard_bp.route('/preguntas')
def preguntas():
    return render_template('dashboard/preguntasFrecuentes.html')

@dashboard_bp.route('/registro')
def registro():
    return render_template('auth/register.html')

@dashboard_bp.route('/login')
def login():
    return render_template('auth/login.html')

@dashboard_bp.route('/perfil')
def perfil():
    if 'email' in session:
        users = cargar_users_jsonbin()
        usuario_logueado = next((user for user in users if user['email'] == session['email']), None)

        if usuario_logueado:
            return render_template('dashboard/miPerfil.html', user=usuario_logueado)
    
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/recetas')
def recetas():
    return render_template('dashboard/recetas.html')

@dashboard_bp.route('/cursos')
def cursos():
    return render_template('dashboard/cursos.html')

@dashboard_bp.route('/vercurso')
def vercurso():
    return render_template('dashboard/verCurso.html')

@dashboard_bp.route('/verreceta')
def verreceta():
    return render_template('dashboard/verReceta.html')

@dashboard_bp.route('/subirreceta')
def subirreceta():
    return render_template('dashboard/subirReceta.html')

@dashboard_bp.route('/subircurso', methods=['POST', 'GET'])
def subircurso():
    if request.method == 'POST':
        titulo_curso = request.form['titulo_curso']
        lugar = request.form['lugar']
        cupos = request.form['cupos']
        precio = request.form['precio']
        fecha = request.form['fecha']
        hora = request.form['hora']
        dificultad = request.form.get('dificultad', None)
        desCurso = request.form['desCurso']

        if not lugar or not titulo_curso or not cupos or not precio or not fecha or not hora or not dificultad or not desCurso:
            return jsonify({'mensaje':'Los campos no pueden estar vacíos'}), 400
        
        response = requests.get(JSONBIN_URL, headers= HEADERS)
        cursos = response.json().get('record', {}).get('record', [])

        nuevoCurso = {
            'titulo': titulo_curso,
            'lugar': lugar,
            'cupos_disponibles': cupos,
            'precio': precio,
            'fecha': fecha,
            'descripcion': desCurso,
            'hora': hora,
            'dificultad': dificultad
        }

        cursos.append(nuevoCurso)
        response = requests.put(JSONBIN_URL, json={'record':cursos}, headers=HEADERS)
        if response.status_code==200:
            return render_template("index.html")
        else:
            return jsonify({'mensaje': 'no se pudo añadir'}), 500

    return render_template('dashboard/subirCurso.html')