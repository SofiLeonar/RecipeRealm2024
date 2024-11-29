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
    if 'userid' not in session: 
        flash('Por favor, inicia sesión para editar un curso.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form['titulo_curso']
        lugar = request.form['lugar']
        cupos_disponibles = request.form['cupos']
        precio = request.form['precio']
        fecha = request.form['fecha']
        descripcion = request.form['desCurso']
        hora = request.form['hora']
        dificultad = request.form['dificultad']
        
        foto_url = None
        foto = request.files.get('foto')
        
        if foto:
            try:
                upload_result = cloudinary.uploader.upload(foto)
                foto_url = upload_result['url']
            except Exception as e:
                flash(f'Error al subir la foto: {str(e)}')
                return redirect(url_for('dashboard_bp.editarcurso', curso_id=curso_id))
        
        cursor = mysql.connection.cursor()
        
        try:
            if foto_url:
                cursor.execute("""
                    UPDATE cursos 
                    SET titulo = %s, lugar = %s, cupos_disponibles = %s, precio = %s, fecha = %s, 
                        descripcion = %s, hora = %s, dificultad = %s, foto = %s 
                    WHERE id = %s
                """, (titulo, lugar, cupos_disponibles, precio, fecha, descripcion, hora, dificultad, foto_url, curso_id))
            else:
                cursor.execute("""
                    UPDATE cursos 
                    SET titulo = %s, lugar = %s, cupos_disponibles = %s, precio = %s, fecha = %s, 
                        descripcion = %s, hora = %s, dificultad = %s
                    WHERE id = %s
                """, (titulo, lugar, cupos_disponibles, precio, fecha, descripcion, hora, dificultad, curso_id))
            
            mysql.connection.commit()
            flash('Curso actualizado con éxito.')
            return redirect(url_for('dashboard_bp.get_curso_by_id', curso_id=curso_id))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el curso: {str(e)}')
        finally:
            cursor.close()
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, titulo, lugar, cupos_disponibles, precio, fecha, descripcion, hora, dificultad, foto FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
    except Exception as e:
        flash(f'Error al cargar los datos del curso: {str(e)}')
        curso = None
    finally:
        cursor.close()
    
    if not curso:
        flash('No se encontró el curso.')
        return redirect(url_for('dashboard_bp.cursos'))
    
    curso_data = {
        'id': curso[0],
        'titulo': curso[1],
        'lugar': curso[2],
        'cupos_disponibles': curso[3],
        'precio': curso[4],
        'fecha': curso[5],
        'descripcion': curso[6],
        'hora': curso[7],
        'dificultad': curso[8],
        'foto': curso[9],
    }

    return render_template('dashboard/editarCurso.html', curso=curso_data)


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


@dashboard_bp.route('/vercurso')
def vercurso():
    return render_template('dashboard/verCurso.html')


@dashboard_bp.route('/receta/<int:receta_id>')
def get_receta_by_id(receta_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            SELECT 
                r.id, 
                r.titulo_receta, 
                r.lista_ingredientes, 
                r.lista_categorias, 
                r.descripcion, 
                r.foto, 
                u.id as creador_id, 
                u.nombre as creador_nombre, 
                u.foto as creador_foto 
            FROM recetas r 
            JOIN usuarios u ON r.userid = u.id 
            WHERE r.id = %s
            """, 
            (receta_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result:
            receta_info = {
                'id': result[0],
                'titulo_receta': result[1],
                'lista_ingredientes': result[2],
                'lista_categorias': result[3],
                'descripcion': result[4],
                'foto': result[5],
                'creador': {
                    'id': result[6],
                    'nombre': result[7],
                    'foto': result[8]
                }
            }
            return render_template('dashboard/verReceta.html', receta=receta_info)
        else:
            flash('Receta no encontrada.')
            return redirect(url_for('dashboard_bp.recetas'))
    except Exception as e:
        flash(f'Error al obtener la receta: {str(e)}')
        return redirect(url_for('dashboard_bp.recetas'))


def verreceta():
    return render_template('dashboard/verReceta.html')

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


@dashboard_bp.route('/subircurso', methods=['POST', 'GET'])
def subircurso():
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
