from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api

auth_bp = Blueprint('auth', __name__)
#falta esconder las keys
JSONBIN_URL = 'https://api.jsonbin.io/v3/b/67056a8fad19ca34f8b50970'
HEADERS = {
    'Content-Type': 'application/json',
    'X-Master-Key': '$2a$10$1UFHJ7B89yDmWCd/HBP5xO1idjuzb0siHyQ2QNroWFWeO74FLn5Fi'
}

cloudinary.config( 
    cloud_name = "dy6qn93sv", 
    api_key = "584855744426521", 
    api_secret = "4_eMIemyI3f04WuqopVeqdqMUKQ", 
    secure=True
)

def cargar_users_jsonbin():
    try:
        response = requests.get(JSONBIN_URL, headers=HEADERS)
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
        response = requests.put(JSONBIN_URL, headers=HEADERS, json=update_data)
        if response.status_code == 200:
            flash('Usuario registrado correctamente.')
        else:
            flash('Error al guardar el nuevo usuario.')
    except Exception as e:
        flash(f'Error al guardar usuario en JSONBin: {str(e)}')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        chef = request.form['chef']
        bio = request.form['bio']
        foto = request.files.get('foto')

        if foto:
            upload_result = cloudinary.uploader.upload(foto)
            foto_url = upload_result['url']  
        else:
            foto_url = None 
            
        is_chef = True if chef == 'True' else False
        
        users = cargar_users_jsonbin()
        for user in users: 
            if user['email'] == email: 
                flash('Este correo ya está registrado. Intenta con otro.')
                return redirect(url_for('auth.register'))
            
       

        nuevo_usuario = {
            'email': email,
            'password': password,  
            'nombre': nombre,
            'usuario': usuario,
            'chef': is_chef,
            'bio': bio,
            'foto': foto_url
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
                return redirect(url_for('auth.protected'))

        flash('Correo o contraseña incorrectos.')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/protected')
def protected():
    if 'email' in session:
        return render_template('protected.html', email=session['email'])
    else:
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))
