from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
import re
import mysql.connector
from flask_mysqldb import MySQL
from app import mysql


auth_bp = Blueprint('auth', __name__)

cloudinary.config( 
    cloud_name = "dy6qn93sv", 
    api_key = "584855744426521", 
    api_secret = "4_eMIemyI3f04WuqopVeqdqMUKQ", 
    secure=True
)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error_nombre = None
    error_usuario = None
    error_email = None
    error_password = None
    error_bio = None
    error_foto = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        chef = request.form['chef']
        bio = request.form['bio']
        foto = request.files.get('foto')

        # Validaciones
        if len(usuario) <= 3:
            error_usuario = 'El pseudónimo debe tener más de 3 caracteres.'

        if len(bio) <= 10:
            error_bio = 'La descripción debe tener más de 10 caracteres.'

        if len(nombre) <= 3:
            error_nombre = 'El nombre debe tener más de 3 caracteres.'

        if len(password) < 8 or not re.search(r'[A-Z]', password):
            error_password = 'La contraseña debe tener al menos 8 caracteres y contener al menos una letra mayúscula.'

        foto_url = None
        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']

        is_chef = 'Chef' if chef == 'True' else 'Aficionado'

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()
        if usuario_existente:
            error_email = 'Este correo ya está registrado. Intenta con otro.'

        if error_nombre or error_usuario or error_email or error_password or error_bio:
            return render_template('auth/register.html',
                                   error_nombre=error_nombre,
                                   error_usuario=error_usuario,
                                   error_email=error_email,
                                   error_password=error_password,
                                   error_bio=error_bio,
                                   error_foto=error_foto)

        cursor.execute("""
            INSERT INTO usuarios (email, password, nombre, usuario, chef, bio, foto) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (email, password, nombre, usuario, is_chef, bio, foto_url))
        mysql.connection.commit()

        cursor.close()

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        for user in users: 
            if user['email'] == email and user['password'] == password: 
                session['email'] = email 
                session['userid'] = user['userid']
                return redirect(url_for('dashboard_bp.perfil'))

        flash('Correo o contraseña incorrectos.')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/protected')
def protected():
    if 'email' in session:
        usuario_logueado= next((user for user in users if user['email'] == session['email']), None)

        if usuario_logueado:
            return render_template('protected.html', email=session['email'])
    else:
        return redirect(url_for('auth.login'))
    
@auth_bp.route('/eliminarperfil', methods=['GET', 'POST'])
def eliminarperfil():
    if request.method == 'POST':
        email = session.get('email')
        
        updated_users = [user for user in users if user['email'] != email]

        try:
            update_data = {'record': updated_users}
            response = requests.put(JSONBIN_USERS_URL, headers=HEADERS_USERS, json=update_data)
            if response.status_code == 200:
                session.pop('email', None) 
                return redirect(url_for('auth.register')) 
        except Exception as e:
            flash(f'Error al eliminar la cuenta: {str(e)}')

    return render_template('dashboard/miPerfil.html')

@auth_bp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))
