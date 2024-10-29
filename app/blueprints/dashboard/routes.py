from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint, jsonify
import requests
from . import dashboard_bp
from app.blueprints.auth.routes import cargar_users_jsonbin, guardar_usuario_jsonbin
from config import JSONBIN_CURSOS_URL, HEADERS_CURSOS, JSONBIN_USERS_URL, HEADERS_USERS
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
#faltan alertas
cloudinary.config( 
    cloud_name = "dzjpeuzcn", 
    api_key = "859251897787294", 
    api_secret = "sxJLKRkscHL7ChM-xpbnSdpYUuc",
    secure=True
)

dashboard_bp = Blueprint('dashboard_bp', __name__)
def guardar_usuario_actualizado(email, usuario_actualizado):
    try:
        users = cargar_users_jsonbin()
        usuario_existente = next((user for user in users if user['email'] == email), None)

        if usuario_existente:
            usuario_existente.update(usuario_actualizado)

            update_data = {'record': users}
            response = requests.put(JSONBIN_USERS_URL, headers=HEADERS_USERS, json=update_data)
            if response.status_code == 200:
                flash('Usuario actualizado correctamente.')
            else:
                flash('Error al actualizar el usuario.')
        else:
            flash('Usuario no encontrado.')

    except Exception as e:
        flash(f'Error al actualizar el usuario en JSONBin: {str(e)}')

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

@dashboard_bp.route('/editarperfil', methods=['GET', 'POST'])
def editarperfil():
    if request.method == 'POST':
        users = cargar_users_jsonbin()
        usuario_logueado = next((user for user in users if user['email'] == session['email']), None)

        if usuario_logueado:
            usuario_actualizado = {
                'nombre': request.form['nombre'],
                'usuario': request.form['usuario'],
                'bio': request.form['bio'],
                'chef': 'Chef' if request.form['chef'] == 'True' else 'Aficionado',
            }

            foto = request.files.get('foto')
            if foto:
                try:
                    upload_result = cloudinary.uploader.upload(foto)
                    usuario_actualizado['foto'] = upload_result['url']
                except Exception as e:
                    flash('Error al subir la foto. Por favor, intentá de nuevo.')
                    return redirect(url_for('dashboard_bp.editarperfil'))

            guardar_usuario_actualizado(usuario_logueado['email'], usuario_actualizado)

            return redirect(url_for('dashboard_bp.perfil'))

    users = cargar_users_jsonbin()
    usuario_logueado = next((user for user in users if user['email'] == session['email']), None)

    if not usuario_logueado:
        flash('No se pudo cargar el perfil del usuario.')
        return redirect(url_for('auth.login'))

    return render_template('dashboard/editarPerfil.html', user=usuario_logueado)


@dashboard_bp.route('/recetas')
def recetas():
    return render_template('dashboard/recetas.html')

@dashboard_bp.route('/cursos')
def cursos():
    response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)
    cursos = response.json().get('record', {}).get('record', []) 
    return render_template('dashboard/cursos.html', cursosInfo=cursos)


@dashboard_bp.route('/curso/<int:curso_id>', methods=['GET'])
def get_curso_by_id(curso_id):
    try:
        response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)

        if response.status_code != 200:
            print(f"Error al obtener datos de JSONBIN: {response.status_code} - {response.text}")
            return jsonify({"error": "Error al obtener datos de JSONBIN"}), 500

        data = response.json()

        print("Contenido de la respuesta JSON:", data)

        records = data.get('record', {}).get('record', [])

        for curso in records:
            if curso.get('id') == curso_id:
                print(f"Curso encontrado: {curso}")
                return render_template('dashboard/verCurso.html', curso=curso)
        
        print(f"Curso con ID {curso_id} no encontrado.")
        return jsonify({"error": "Curso no encontrado"}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/vercurso')
def vercurso():

    return render_template('dashboard/verCurso.html')

@dashboard_bp.route('/verreceta')
def verreceta():
    return render_template('dashboard/verReceta.html')

@dashboard_bp.route('/subirreceta')
def subirreceta():
    return render_template('dashboard/subirReceta.html')

def validar_curso(titulo_curso, lugar, cupos, precio, fecha, hora, dificultad, desCurso):
    if not lugar or not titulo_curso or not cupos or not precio or not fecha or not hora or not dificultad or not desCurso:
        return jsonify({'mensaje': 'Todos los campos son obligatorios'}), 400

    try:
        cupos = int(cupos)
        precio = float(precio) 
    except ValueError:
        return jsonify({'mensaje': 'Formato de datos inválido'}), 400

    if len(titulo_curso) > 100:
        return jsonify({'mensaje': 'El título del curso es demasiado largo'}), 400

    return None, 200

def guardar_curso(cursos, nuevoCurso):
    cursos.append(nuevoCurso)
    response = requests.put(JSONBIN_CURSOS_URL, json={'record': cursos}, headers=HEADERS_CURSOS)
    if response.status_code == 200:
        return render_template("dashboard/cursos.html")
    else:
        return jsonify({'mensaje': 'No se pudo añadir el curso'}), 500

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
        foto = request.files.get('foto')

        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']
        else:
            foto_url = None

        
        error, status_code = validar_curso(titulo_curso, lugar, cupos, precio, fecha, hora, dificultad, desCurso)
        if error:
            return error, status_code

        response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)
        try:
            cursos = response.json().get('record', {}).get('record', [])
        except ValueError:
            return jsonify({"error": "Error al obtener los datos"}), 500


        if cursos:
            nuevo_id = max(int(curso.get('id', 0)) for curso in cursos if 'id' in curso) + 1
        else:
            nuevo_id = 1

        userid = session.get('userid')
        nuevoCurso = {
            'id': nuevo_id,
            'titulo': titulo_curso,
            'lugar': lugar,
            'cupos_disponibles': cupos,
            'precio': precio,
            'fecha': fecha, 
            'descripcion': desCurso,
            'hora': hora,
            'dificultad': dificultad,
            'foto': foto_url,
            'userid': userid
        }

        return guardar_curso(cursos, nuevoCurso)

    return render_template('dashboard/subirCurso.html')
