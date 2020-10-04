from flask import Flask
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
bcryp = Bcrypt()
jwt = JWTManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:palafox88@localhost/orm_exa'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAPBOX_MAP_ID'] = "example.abc123"
    app.config['JWT_SECRET_KEY'] = 'secret'

    db.init_app(app)
    ma.init_app(app)
    bcryp.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        db.create_all()

    # Registro de los Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .events import event_bp
    app.register_blueprint(event_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    return app

    