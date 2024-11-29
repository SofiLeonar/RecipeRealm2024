from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint, jsonify
import requests
import json
from . import dashboard_bp
from config import JSONBIN_CURSOS_URL, HEADERS_CURSOS, JSONBIN_USERS_URL, HEADERS_USERS, JSONBIN_RECETAS_URL
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask_mysqldb import MySQL
from app import mysql


cloudinary.config( 
    cloud_name = "dzjpeuzcn", 
    api_key = "859251897787294", 
    api_secret = "sxJLKRkscHL7ChM-xpbnSdpYUuc",
    secure=True
)

dashboard_bp = Blueprint('dashboard_bp', __name__)
"""
def guardar_usuario_actualizado(email, usuario_actualizado):
    try:
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
        flash(f'Error al actualizar el usuario en JSONBin: {str(e)}')"""

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

"""
@dashboard_bp.route('/perfil')
def perfil():
    if 'email' in session:
        usuario_logueado = next((user for user in users if user['email'] == session['email']), None)

        if usuario_logueado:
            return render_template('dashboard/miPerfil.html', user=usuario_logueado)
    
    return redirect(url_for('auth.login'))"""
@dashboard_bp.route('/perfil')
def perfil():
    if 'userid' in session:
        user_id = session['userid']
        
        cursor = mysql.connection.cursor()

        try:
            cursor.execute("SELECT id, email, nombre, usuario, chef, bio, foto FROM usuarios WHERE id = %s", (user_id,))
            usuario_logueado = cursor.fetchone()
        except Exception as e:
            flash(f'Error al cargar el perfil: {str(e)}')
            usuario_logueado = None
        finally:
            cursor.close()

        if usuario_logueado:
            user_data = {
                'id': usuario_logueado[0],
                'email': usuario_logueado[1],
                'nombre': usuario_logueado[2],
                'usuario': usuario_logueado[3],
                'chef': usuario_logueado[4],
                'bio': usuario_logueado[5],
                'foto': usuario_logueado[6],
            }
            return render_template('dashboard/miPerfil.html', user=user_data)
    
    return redirect(url_for('auth.login'))
"""
@dashboard_bp.route('/editarperfil', methods=['GET', 'POST'])
def editarperfil():
    if request.method == 'POST':
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

    usuario_logueado = next((user for user in users if user['email'] == session['email']), None)

    if not usuario_logueado:
        flash('No se pudo cargar el perfil del usuario.')
        return redirect(url_for('auth.login'))

    return render_template('dashboard/editarPerfil.html', user=usuario_logueado)
"""

@dashboard_bp.route('/editarperfil', methods=['GET', 'POST'])
def editarperfil():
    if 'userid' not in session: 
        flash('Por favor, inicia sesión para editar tu perfil.')
        return redirect(url_for('auth.login'))

    user_id = session['userid']

    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        bio = request.form['bio']
        chef = 'Chef' if request.form.get('chef') == 'True' else 'Aficionado'

        foto_url = None
        foto = request.files.get('foto')

        if foto:
            try:
                upload_result = cloudinary.uploader.upload(foto)
                foto_url = upload_result['url']
            except Exception as e:
                flash(f'Error al subir la foto: {str(e)}')
                return redirect(url_for('dashboard_bp.editarperfil'))

        cursor = mysql.connection.cursor()

        try:
            if foto_url: 
                cursor.execute("UPDATE usuarios SET nombre = %s, usuario = %s, bio = %s, chef = %s, foto = %s WHERE id = %s", (nombre, usuario, bio, chef, foto_url, user_id))
            else:  
                cursor.execute("UPDATE usuarios SET nombre = %s, usuario = %s, bio = %s, chef = %s WHERE id = %s", (nombre, usuario, bio, chef, user_id))
            mysql.connection.commit()
            flash('Perfil actualizado con éxito.')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el perfil: {str(e)}')
        finally:
            cursor.close()

        return redirect(url_for('dashboard_bp.perfil'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, email, nombre, usuario, bio, chef, foto FROM usuarios WHERE id = %s", (user_id,))
        usuario_logueado = cursor.fetchone()
    except Exception as e:
        flash(f'Error al cargar los datos del usuario: {str(e)}')
        usuario_logueado = None
    finally:
        cursor.close()

    if not usuario_logueado:
        flash('No se pudo cargar el perfil del usuario.')
        return redirect(url_for('auth.login'))

    user_data = {
        'id': usuario_logueado[0],
        'email': usuario_logueado[1],
        'nombre': usuario_logueado[2],
        'usuario': usuario_logueado[3],
        'bio': usuario_logueado[4],
        'chef': usuario_logueado[5],
        'foto': usuario_logueado[6],
    }

    return render_template('dashboard/editarPerfil.html', user=user_data)

@dashboard_bp.route('/recetas')
def recetas():
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("SELECT id, titulo_receta, foto FROM recetas")
        recetas_info = cursor.fetchall()

        recetas_info = [{'id': receta[0], 'titulo_receta': receta[1], 'foto': receta[2]} for receta in recetas_info]
        
        print(f'Recetas cargadas: {recetas_info}')
        
        if not recetas_info:
            flash('No se encontraron recetas disponibles.', 'warning')
            print('No se encontraron recetas disponibles.')
            
    except Exception as e:
        flash(f'Error al cargar las recetas: {str(e)}', 'error')
        print(f'Error al cargar las recetas: {str(e)}') 
        recetas_info = []

    finally:
        cursor.close()

    print(f'Información de recetas a pasar al template: {recetas_info}')
    return render_template('dashboard/recetas.html', recetasInfo=recetas_info)


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
    

@dashboard_bp.route('/eliminarcurso', methods=['POST', 'GET'])
def eliminarcurso():
    curso_id = request.form.get('curso_id')
    if not curso_id:
        flash('No se especificó el curso a eliminar.', 'error')
        return redirect(url_for('dashboard_bp.cursos'))

    try:
        response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)
        data = response.json()
        cursos = data.get('record', {}).get('record', []) 

        updated_cursos = [curso for curso in cursos if str(curso.get('id')) != curso_id]

        update_data = {'record': updated_cursos}
        response = requests.put(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS, json=update_data)

        if response.status_code == 200:
            flash('Curso eliminado correctamente.', 'success')
        else:
            flash('Error al eliminar el curso.', 'error')

    except Exception as e:
        flash(f'Error al eliminar el curso: {str(e)}', 'error')

    return redirect(url_for('dashboard_bp.cursos'))


@dashboard_bp.route('/editarcurso/<int:curso_id>', methods=['GET', 'POST'])
def editarcurso(curso_id):
    response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)
    data = response.json()
    cursos = data.get('record', {}).get('record', [])

    curso = next((c for c in cursos if c['id'] == curso_id), None)
    
    if not curso:
        flash('Curso no encontrado.')
        return redirect(url_for('dashboard_bp.cursos'))

    if request.method == 'POST':
        curso_actualizado = {
            'titulo': request.form['titulo_curso'],
            'lugar': request.form['lugar'],
            'cupos_disponibles': request.form['cupos'],
            'precio': request.form['precio'],
            'fecha': request.form['fecha'],
            'descripcion': request.form['desCurso'],
            'hora': request.form['hora'],
            'dificultad': request.form['dificultad'],
        }

        foto = request.files.get('foto')
        if foto:
            try:
                upload_result = cloudinary.uploader.upload(foto)
                curso_actualizado['foto'] = upload_result['url']
            except Exception as e:
                flash('Error al subir la foto. Por favor, intenta de nuevo.')
                return redirect(url_for('dashboard_bp.editarcurso', curso_id=curso_id))

        for i, c in enumerate(cursos):
            if c['id'] == curso_id:
                cursos[i].update(curso_actualizado)
                break

        response = requests.put(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS, json={'record': cursos})
        if response.status_code == 200:
            flash('Curso actualizado correctamente.')
            return redirect(url_for('dashboard_bp.get_curso_by_id', curso_id=curso_id))
        else:
            flash('Error al actualizar el curso.')

    return render_template('dashboard/editarCurso.html', curso=curso)


@dashboard_bp.route('/vercurso')
def vercurso():
    return render_template('dashboard/verCurso.html')

@dashboard_bp.route('/receta/<int:receta_id>', methods=['GET'])
def get_receta_by_id(receta_id):
    try:
        response = requests.get(JSONBIN_RECETAS_URL, headers=HEADERS_CURSOS)

        if response.status_code != 200:
            print(f"Error al obtener datos de JSONBIN: {response.status_code} - {response.text}")
            return jsonify({"error": "Error al obtener datos de JSONBIN"}), 500

        data = response.json()

        print("Contenido de la respuesta JSON:", data)

        records = data.get('record', {}).get('record', [])

        for receta in records:
            if receta.get('id') == receta_id:
                print(f"Curso encontrado: {receta}")
                return render_template('dashboard/verReceta.html', receta=receta)
        
        print(f"Receta con ID {receta_id} no encontrado.")
        return jsonify({"error": "Receta no encontrado"}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/miscursos')
def miscursos():
    if 'userid' in session:
        response = requests.get(JSONBIN_CURSOS_URL, headers=HEADERS_CURSOS)
        if response.status_code != 200:
            flash('Error al obtener los cursos.')
            return render_template('dashboard/misCursos.html', cursosInfo=[])

        cursos = response.json().get('record', {}).get('record', [])

        userid = session['userid']
        cursos_usuario = [curso for curso in cursos if curso.get('userid') == userid]

        return render_template('dashboard/misCursos.html', cursosInfo=cursos_usuario)

    flash('Debes iniciar sesión para ver tus cursos.')
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/misrecetas')
def misrecetas():
    if 'userid' in session:
        user_id = session['userid']
        print(f'User ID en sesión: {user_id}') 
        
        cursor = mysql.connection.cursor()
        
        try:
            cursor.execute("SELECT id, titulo_receta, foto FROM recetas WHERE userid = %s", (user_id,))
            recetas_info = cursor.fetchall()

            recetas_info = [{'id': receta[0], 'titulo_receta': receta[1], 'foto': receta[2]} for receta in recetas_info]
            
            print(f'Recetas cargadas: {recetas_info}')
            
            if not recetas_info:
                flash('No se encontraron recetas para este usuario.', 'warning')
                print('No se encontraron recetas para este usuario.')  
            
        except Exception as e:
            flash(f'Error al cargar las recetas: {str(e)}', 'error')
            print(f'Error al cargar las recetas: {str(e)}') 
            recetas_info = []

        finally:
            cursor.close()

        print(f'Información de recetas a pasar al template: {recetas_info}')
        return render_template('dashboard/recetas.html', recetasInfo=recetas_info)
    
    print("No se encontró el User ID en la sesión, redirigiendo al login.") 
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/verreceta')
def verreceta():
    return render_template('dashboard/verReceta.html')

def validar_receta(titulo_receta, listaIngredientes, listaCategorias, descripcion):
    error_messages = []

    if not titulo_receta or not listaIngredientes or not listaCategorias or not descripcion:
        error_messages.append('Todos los campos son obligatorios.')

    if len(titulo_receta) > 100:
        error_messages.append('El título de la receta es demasiado largo.')

    if len(descripcion) > 2000:
        error_messages.append('La descripción se excede de 2000 caracteres.')

    if error_messages:
        return error_messages

    return None

@dashboard_bp.route('/subirreceta', methods=['POST', 'GET'])
def subirreceta():
    if request.method == 'POST':
        titulo_receta = request.form['titulo']
        lista_ingredientes = request.form['listaIngredientes']
        lista_categorias = request.form['listaCategorias']
        descripcion = request.form['descripcion']
        foto = request.files.get('foto')

        validation_errors = validar_receta(titulo_receta, lista_ingredientes, lista_categorias, descripcion)
        
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('dashboard/subirReceta.html')

        if not foto:
            flash("La foto es obligatoria.", 'error')
            return render_template('dashboard/subirReceta.html')

        try:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']
        except Exception as e:
            flash(f"Error al subir la imagen: {str(e)}", 'error')
            return render_template('dashboard/subirReceta.html')

        userid = session.get('userid')
        if not userid:
            flash("Usuario no autenticado.", 'error')
            return render_template('dashboard/subirReceta.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO recetas (titulo_receta, lista_ingredientes, lista_categorias, descripcion, foto, userid) VALUES (%s, %s, %s, %s, %s, %s)",
                (titulo_receta, lista_ingredientes, lista_categorias, descripcion, foto_url, userid)
            )
            mysql.connection.commit()
            flash('¡Tu receta se subió con éxito!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al guardar la receta: {str(e)}', 'error')
        finally:
            cursor.close()

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
        return redirect(url_for('dashboard_bp.cursos'))
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
