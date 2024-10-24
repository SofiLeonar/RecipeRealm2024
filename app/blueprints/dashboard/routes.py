from flask import render_template
from . import dashboard_bp

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
    return render_template('dashboard/miPerfil.html')

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