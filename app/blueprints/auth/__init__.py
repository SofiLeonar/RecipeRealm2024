from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefilx='/auth')

from . import routes
