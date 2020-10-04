from flask import request, jsonify
from datetime import datetime
from flask_jwt_extended import create_access_token
from app.auth.models import Users

from app import db, socketio, bcryp

def register():
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password = bcryp.generate_password_hash(request.get_json()['password']).decode('utf-8')
    created = datetime.utcnow()
    user = Users(first_name=first_name, last_name=last_name, email=email, password=password, created=created)
    db.session.add(user)
    db.session.commit()
    return 'todo bien'

def login():
    email = request.get_json()['email']
    password = request.get_json()['password']
    user = Users.query.filter_by(email=email).first()
    if bcryp.check_password_hash(user.password, password):
        access_token = create_access_token(identity = {'id': user.id,'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})
        result = jsonify({"token":access_token})
    else:
        result = jsonify({"error":"email o contraseña invalidos"})
    return result