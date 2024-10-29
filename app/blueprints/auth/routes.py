from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import JSONBIN_USERS_URL, HEADERS_USERS
import uuid
import re

auth_bp = Blueprint('auth', __name__)

cloudinary.config( 
    cloud_name = "dy6qn93sv", 
    api_key = "584855744426521", 
    api_secret = "4_eMIemyI3f04WuqopVeqdqMUKQ", 
    secure=True
)

def cargar_users_jsonbin():
    try:
        response = requests.get(JSONBIN_USERS_URL, headers=HEADERS_USERS)
        if response.status_code == 200:
            data = response.json()
            users = data.get('record', {}).get('record', []) 
            return users 
        else:
            flash('Error al cargar usuarios del JSONBin.')
            return []
    except Exception as e:
        flash(f'Error al acceder a JSONBin: {str(e)}')
        return []


def guardar_usuario_jsonbin(nuevo_usuario):
    try:
        users = cargar_users_jsonbin()  
        users.append(nuevo_usuario)
        update_data = {'record': users} 
        response = requests.put(JSONBIN_USERS_URL, headers=HEADERS_USERS, json=update_data)
        if response.status_code == 200:
            print('Usuario registrado correctamente.')
        else:
            print('Error al guardar el nuevo usuario.')
    except Exception as e:
        flash(f'Error al guardar usuario en JSONBin: {str(e)}')

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
        userid = str(uuid.uuid4())

        # validaciones
        if len(usuario) <= 3:
            error_usuario = 'El pseudónimo debe tener más de 3 caracteres.'
        
        if len(bio) <= 10:
            error_bio = 'La descripción debe tener más de 10 caracteres.'
        
        if len(nombre) <= 3:
            error_nombre = 'El nombre debe tener más de 3 caracteres.'
        
        if len(password) < 8 or not re.search(r'[A-Z]', password):
            error_password = 'La contraseña debe tener al menos 8 caracteres y contener al menos una letra mayúscula.'
        
        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']
        else:
            foto_url = None
        
        is_chef = 'Chef' if chef == 'True' else 'Aficionado'
        
        users = cargar_users_jsonbin()
        for user in users: 
            if user['email'] == email: 
                error_email = 'Este correo ya está registrado. Intenta con otro.'
                break
        
        if error_nombre or error_usuario or error_email or error_password or error_bio:
            return render_template('auth/register.html', 
                                   error_nombre=error_nombre, 
                                   error_usuario=error_usuario, 
                                   error_email=error_email, 
                                   error_password=error_password, 
                                   error_bio=error_bio, 
                                   error_foto=error_foto)

        nuevo_usuario = {
            'email': email,
            'password': password,  
            'nombre': nombre,
            'usuario': usuario,
            'chef': is_chef,
            'bio': bio,
            'foto': foto_url,            
            'userid': userid,
        }

        guardar_usuario_jsonbin(nuevo_usuario) 
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = cargar_users_jsonbin()

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
        users = cargar_users_jsonbin()
        usuario_logueado= next((user for user in users if user['email'] == session['email']), None)

        if usuario_logueado:
            return render_template('protected.html', email=session['email'])
    else:
        return redirect(url_for('auth.login'))
    
@auth_bp.route('/eliminarperfil', methods=['GET', 'POST'])
def eliminarperfil():
    if request.method == 'POST':
        email = session.get('email')
        users = cargar_users_jsonbin()
        
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
