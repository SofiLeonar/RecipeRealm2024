from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint, jsonify
import requests
import json
from . import dashboard_bp
from config import JSONBIN_CURSOS_URL, HEADERS_CURSOS, JSONBIN_USERS_URL, HEADERS_USERS, JSONBIN_RECETAS_URL
import cloudinary
import cloudinary.uploader
import cloudinary.api
import mysql.connector
import pymysql
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
                cursor.execute("UPDATE usuarios SET nombre = %s, usuario = %s, bio = %s, foto = %s WHERE id = %s", (nombre, usuario, bio, foto_url, user_id))
            else:  
                cursor.execute("UPDATE usuarios SET nombre = %s, usuario = %s, bio = %s,  WHERE id = %s", (nombre, usuario, bio, user_id))
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
    response = requests.get(JSONBIN_RECETAS_URL, headers=HEADERS_CURSOS)
    recetas = response.json().get('record', {}).get('record', []) 
    return render_template('dashboard/recetas.html', recetasInfo=recetas)

@dashboard_bp.route('/cursos')
def cursos():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, titulo, descripcion, precio, dificultad, fecha, foto FROM cursos") 
        cursos = cursor.fetchall()
        
        cursos_info = []
        for curso in cursos:
            curso_data = {
                'id': curso[0],
                'titulo': curso[1],
                'descripcion': curso[2],
                'precio': curso[3],
                'dificultad': curso[4],
                'fecha': curso[5],
                'foto': curso[6]
            }
            cursos_info.append(curso_data)
        cursor.close()

        return render_template('dashboard/cursos.html', cursosInfo=cursos_info)

    except Exception as e:
        flash(f'Error al obtener los cursos: {str(e)}')
        return render_template('dashboard/cursos.html', cursosInfo=[])

"""
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
    """


@dashboard_bp.route('/eliminarcurso', methods=['POST'])
def eliminarcurso():
    if 'userid' not in session:
        flash('Debes iniciar sesión para realizar esta acción.', 'error')
        return redirect(url_for('auth.login'))

    curso_id = request.form.get('curso_id')

    if not curso_id:
        flash('No se especificó el curso a eliminar.', 'error')
        return redirect(url_for('dashboard_bp.cursos'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id FROM cursos WHERE id = %s AND userid = %s", (curso_id, session['userid']))
        curso = cursor.fetchone()

        if curso:
            print(f"Curso encontrado: {curso}")
        else:
            print("Curso no encontrado o no pertenece al usuario.")
            flash('No tienes permiso para eliminar este curso o no existe.', 'error')
            return redirect(url_for('dashboard_bp.cursos'))

        cursor.execute("DELETE FROM cursos WHERE id = %s AND userid = %s", (curso_id, session['userid']))
        mysql.connection.commit()

        flash('Curso eliminado correctamente.', 'success')

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Ocurrió un error al eliminar el curso: {str(e)}', 'error')
    finally:
        cursor.close()

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


@dashboard_bp.route('/curso/<int:curso_id>')
def get_curso_by_id(curso_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT c.id, c.titulo, c.descripcion, c.precio, c.dificultad, c.fecha, c.hora, c.lugar, c.foto, c.cupos_disponibles, u.id as instructor_id, u.nombre as instructor_nombre, u.foto as instructor_foto FROM cursos c JOIN usuarios u ON c.userid = u.id WHERE c.id = %s", 
            (curso_id,)
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            curso_info = {
                'id': result[0],
                'titulo': result[1],
                'descripcion': result[2],
                'precio': result[3],
                'dificultad': result[4],
                'fecha': result[5],
                'hora': result[6],
                'lugar': result[7],
                'foto': result[8],
                'cupos_disponibles': result[9],
                'instructor': {
                    'id': result[10],
                    'nombre': result[11],
                    'foto': result[12]
                }
            }
            return render_template('dashboard/verCurso.html', curso=curso_info)

        else:
            flash('Curso no encontrado.')
            return redirect(url_for('dashboard_bp.cursos'))

    except Exception as e:
        flash(f'Error al obtener el curso: {str(e)}')
        return redirect(url_for('dashboard_bp.cursos'))


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
    if 'userid' not in session:
        flash('Debes iniciar sesión para ver tus cursos.')
        return redirect(url_for('auth.login'))

    user_id = session['userid']

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, titulo, descripcion, precio, dificultad, fecha, foto FROM cursos WHERE userid = %s", (user_id,))
        cursos_usuario = cursor.fetchall()
        cursor.close()
        
        if cursos_usuario:
            cursos_info = []
            for curso in cursos_usuario:
                curso_data = {
                    'id': curso[0],
                    'titulo': curso[1],
                    'descripcion': curso[2],
                    'precio': curso[3],
                    'dificultad': curso[4],
                    'fecha': curso[5],
                    'foto': curso[6]
                }
                cursos_info.append(curso_data)

            return render_template('dashboard/misCursos.html', cursosInfo=cursos_info)

        else:
            flash('No tienes cursos publicados.')
            return render_template('dashboard/misCursos.html', cursosInfo=[])

    except Exception as e:
        flash(f'Error al obtener los cursos: {str(e)}')
        return render_template('dashboard/misCursos.html', cursosInfo=[])


@dashboard_bp.route('/misrecetas')
def misrecetas():
    if 'userid' in session:
        response = requests.get(JSONBIN_RECETAS_URL, headers=HEADERS_CURSOS)
        if response.status_code != 200:
            flash('Error al obtener las recetas.')
            return render_template('dashboard/misRecetas.html', recetasInfo=[])

        recetas = response.json().get('record', {}).get('record', [])

        userid = session['userid']
        recetas_usuario = [receta for receta in recetas if receta.get('userid') == userid]

        return render_template('dashboard/misRecetas.html', recetasInfo=recetas_usuario)

    flash('Debes iniciar sesión para ver tus recetas.')
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/verreceta')
def verreceta():
    return render_template('dashboard/verReceta.html')

def validar_receta(titulo_receta, listaIngredientes, listaCategorias, descripcion):
    if not titulo_receta  or not listaIngredientes or not listaCategorias or not descripcion:
        return jsonify({'mensaje': 'Todos los campos son obligatorios'}), 400

    if len(titulo_receta) > 100:
        return jsonify({'mensaje': 'El título del curso es demasiado largo'}), 400
    if len(descripcion) > 2000:
        return jsonify({'mensaje': 'La descripción se excede de 2000 caracteres'}), 400

    return None, 200

"""def guardar_receta(recetas, nuevaReceta):
    recetas.append(nuevaReceta)
    response = requests.put(JSONBIN_RECETAS_URL, json={'record': recetas}, headers=HEADERS_CURSOS)
    if response.status_code == 200:
        return redirect(url_for('dashboard_bp.recetas'))
    else:
        return jsonify({'mensaje': 'No se pudo añadir la receta'}), 500"""

"""@dashboard_bp.route('/subirreceta',  methods=['POST', 'GET'])
def subirreceta():
    if request.method == 'POST':
        titulo_receta = request.form['titulo']
        listaIngredientes = request.form['listaIngredientes'].split(',')
        listaCategorias = request.form['listaCategorias'].split(',')
        descripcion = request.form['descripcion']
        foto = request.files.get('foto')

        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']
        else:
            foto_url = None

        
        error, status_code = validar_receta(titulo_receta, listaIngredientes, listaCategorias, descripcion)
        if error:
            return error, status_code

        response = requests.get(JSONBIN_RECETAS_URL, headers=HEADERS_CURSOS)
        try:
            recetas = response.json().get('record', {}).get('record', [])
        except ValueError:
            return jsonify({"error": "Error al obtener los datos"}), 500


        if recetas:
            nuevo_id = max(int(receta.get('id', 0)) for receta in recetas if 'id' in receta) + 1
        else:
            nuevo_id = 1

        userid = session.get('userid')
        nuevaReceta = {
            'id': nuevo_id,
            'titulo_receta': titulo_receta,
            'listaIngredientes': listaIngredientes,
            'listaCategorias': listaCategorias,
            'descripcion': descripcion,
            'foto': foto_url,
            'userid': userid
        }

        return guardar_receta(recetas, nuevaReceta)
    return render_template('dashboard/subirReceta.html')"""

@dashboard_bp.route('/subirreceta', methods=['POST', 'GET'])
def subirreceta():
    if request.method == 'POST':
        titulo_receta = request.form['titulo']
        listaIngredientes = request.form['listaIngredientes'].split(',')
        listaCategorias = request.form['listaCategorias'].split(',')
        descripcion = request.form['descripcion']
        foto = request.files.get('foto')

        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']
        else:
            foto_url = None

        error, status_code = validar_receta(titulo_receta, listaIngredientes, listaCategorias, descripcion)
        if error:
            return error, status_code

        userid = session.get('userid')
        if not userid:
            return jsonify({"error": "Usuario no autenticado"}), 401

        listaIngredientes = json.dumps(listaIngredientes)
        listaCategorias = json.dumps(listaCategorias)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO recetas (titulo_receta, listaIngredientes, listaCategorias, descripcion, foto, userid) VALUES (%s, %s, %s, %s, %s, %s)",
                (titulo_receta, listaIngredientes, listaCategorias, descripcion, foto_url, userid)
            )
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": "Error al guardar la receta", "detalles": str(e)}), 500
        finally:
            cursor.close()

        return jsonify({"mensaje": "Receta guardada exitosamente"}), 201
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

"""def guardar_curso(cursos, nuevoCurso):
    cursos.append(nuevoCurso)
    response = requests.put(JSONBIN_CURSOS_URL, json={'record': cursos}, headers=HEADERS_CURSOS)
    if response.status_code == 200:
        return redirect(url_for('dashboard_bp.cursos'))
    else:
        return jsonify({'mensaje': 'No se pudo añadir el curso'}), 500
"""
@dashboard_bp.route('/subircurso', methods=['POST', 'GET'])
def subircurso():
    """
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
    """
    if 'userid' not in session:
        flash('Por favor, inicia sesión para subir un curso.')
        return redirect(url_for('auth.login')) 
    
    user_id = session['userid']
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT chef FROM usuarios WHERE id = %s", (user_id,))
    user_role = cursor.fetchone()
    cursor.close()

    if user_role is None or user_role[0] != 'Chef':
        flash('Solo los usuarios con rol de chef pueden subir un curso.')
        return redirect(url_for('dashboard_bp.cursos'))

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

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO cursos (titulo, lugar, cupos_disponibles, precio, fecha, hora, dificultad, descripcion, foto, userid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (titulo_curso, lugar, cupos, precio, fecha, hora, dificultad, desCurso, foto_url, user_id)
                )
            mysql.connection.commit()
            flash('Curso subido exitosamente.')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al subir el curso: {str(e)}')
        finally:
            cursor.close()

        return redirect(url_for('dashboard_bp.miscursos'))

    return render_template('dashboard/subirCurso.html')
