from flask import Flask, render_template
from flask_mysqldb import MySQL
import pymysql
import os
from dotenv import load_dotenv

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD','')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    mysql.init_app(app)

    initialize_database()

    with app.app_context():
        from app.blueprints.auth.routes import auth_bp
        from app.blueprints.dashboard.routes import dashboard_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

def initialize_database():
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    sql_script = """
    CREATE DATABASE IF NOT EXISTS recipeRealm2024;
    USE recipeRealm2024;

    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        nombre VARCHAR(255) NOT NULL,
        usuario VARCHAR(255) NOT NULL,
        chef VARCHAR(50),
        bio TEXT,
        foto TEXT
    );

    CREATE TABLE IF NOT EXISTS recetas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo_receta VARCHAR(255),
        lista_ingredientes TEXT,
        lista_categorias TEXT,
        descripcion TEXT,
        foto VARCHAR(255),
        userid INT,
        FOREIGN KEY (userid) REFERENCES usuarios(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS cursos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(255) NOT NULL,
        lugar VARCHAR(255) NOT NULL,
        cupos_disponibles INT NOT NULL,
        precio DECIMAL(10, 2) NOT NULL,
        fecha DATE NOT NULL,
        descripcion TEXT NOT NULL,
        hora TIME NOT NULL,
        dificultad VARCHAR(255) NOT NULL,
        foto VARCHAR(255) NOT NULL,
        userid INT,
        FOREIGN KEY (userid) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """

    try:
        with connection.cursor() as cursor:
            for statement in sql_script.split(";"):
                if statement.strip():
                    cursor.execute(statement)
        connection.commit()
        print("Base de datos y tablas configuradas correctamente.")
    except Exception as e:
        print(f"Error al configurar la base de datos: {e}")
    finally:
        connection.close()