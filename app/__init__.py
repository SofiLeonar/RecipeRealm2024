from flask import Flask, render_template, request, redirect, url_for
from app.blueprints.auth.routes import auth_bp
from app.blueprints.dashboard.routes import dashboard_bp
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv


mysql = MySQL()

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

    mysql.init_app(app)


    #app.config['SECRET_KEY'] = 'vacac'

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app