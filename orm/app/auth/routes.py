from . import auth_bp
from app.auth.functions import register, login


@auth_bp.route('/users/register', methods=['POST'])
def register_():
    return register()

@auth_bp.route('/users/login', methods=['POST'])
def login_():
    return login()