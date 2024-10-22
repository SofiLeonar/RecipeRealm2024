from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
import requests

auth_bp = Blueprint('auth', __name__)

JSONBIN_URL = 'https://api.jsonbin.io/v3/b/67056a8fad19ca34f8b50970'  
HEADERS = {
    'Content-Type': 'application/json',
    'X-Master-Key': '$2a$10$1UFHJ7B89yDmWCd/HBP5xO1idjuzb0siHyQ2QNroWFWeO74FLn5Fi'
}

def cargar_users_jsonbin():
    try:
        response = requests.get(JSONBIN_URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            users = data.get('record', [])
            return {user['email']: user['password'] for user in users}
        else:
            flash('Error al cargar usuarios desde JSONBin.')
            return {}
    except Exception as e:
        flash(f'Error al acceder a JSONBin: {str(e)}')
        return {}

users = cargar_users_jsonbin()
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['email'] = email
            return redirect(url_for('auth.protected'))
        else:
            flash('Correo o contraseña incorrectos.')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html')

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
