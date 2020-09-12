from flask import Flask, jsonify, request, json, Response, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func

import json

#from db import db_init, db
from models import Users, Picture, Eventos, EventosSchema, db, ma

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:palafox88@localhost/orm_exa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAPBOX_MAP_ID'] = "example.abc123"
app.config['JWT_SECRET_KEY'] = 'secret'

db.init_app(app)
ma.init_app(app)

with app.app_context():
    db.create_all()

bcryp = Bcrypt(app)
jwt = JWTManager(app)
socketio = SocketIO(app)

evento_schema = EventosSchema()
eventos_schema = EventosSchema(many = True)

@app.route('/')
def index():
    return render_template( './AppPage.html' )


def upload(pic):
    if not pic:
        return 'No pic', 400
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    img = Picture(img = pic.read(), name = filename,  mimetype = mimetype)
    db.session.add(img)
    db.session.commit()

    return img.id

@app.route('/users/register', methods=['POST'])
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

@app.route('/users/login', methods=['POST'])
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


@app.route('/event', methods=['POST'])
def event():
    pic = request.files['pic']

    token = request.form['token']
    payload = decode_token(token)
    id_user = str(payload['identity']['id'])
    event_name ='nombre'
    descrip = 'descripcion'
    coorx = 34
    coory = 76
    img = upload(pic)
    date = datetime(2020,8,13,4,50,34)
    coor = 'POINT('+str(coorx)+' '+str(coory)+')'
    print("AQUI MERO")
    print(coor)
    event = Eventos(event_name=event_name, descrip=descrip, coor=coor, id_img=img, date=date, id_user=id_user)
    db.session.add(event)
    db.session.commit()
    check_event()
    print('AQUI MERO')
    print(event.id)
    return str(event.id)

@app.route('/event', methods=['PUT'])
def update_event():
    pic = request.files['pic']
    token = request.form['token']
    payload = decode_token(token)
    id_user = str(payload['identity']['id'])
    _id = request.form['_id']
    event_name ='modificado'
    descrip = 'dess'
    coorx = 34.4352
    coory = 76.2458
    coor = 'POINT('+str(coorx)+' '+str(coory)+')'
    img = upload(pic)
    date = datetime(2020,8,13,4,50,30)

    event = Eventos.query.get(_id)
    event.event_name = event_name
    event.descrip = descrip
    event.coor = coor
    event.id_img = img
    event.date = date
    event.id_user = id_user
    db.session.commit()
    check_event()

    return ('evento actualizado')

@app.route('/list', methods=['POST'])
def list_event():
    event_name = request.get_json()['event_name']
    date = request.get_json()['date']
    lat = request.get_json()['lat']
    lng = request.get_json()['lng']
    dtc = request.get_json()['dtc']
    id_user = request.get_json()['id_user']
    _id = request.get_json()['_id']

    #event = Eventos.query.filter_by(coor='POINT(2 3)').all()
    if event_name:
        event = Eventos.query.filter_by(event_name=event_name).all()
    elif date: 
        event = Eventos.query.filter_by(date=date).all()
    elif lat and lng and dtc:
        event = db.engine.execute("CALL orm("+lat+", "+lng+", "+dtc+")")
    elif id_user:
        event = Eventos.query.filter_by(id_user=id_user).all()
    elif _id:
        event = Eventos.query.filter_by(id=_id).all()
        
    print("A LA MADRE")
    result = eventos_schema.dump(event)
    print("AQUI MEROs")
    print(result[0]['coor'])
    return jsonify(result)

@socketio.on('my event')
def handle_event(json):
    lat = json['lat']
    lng = json['lng']
    dtc = json['dtc']
    event = db.engine.execute("CALL orm("+lat+", "+lng+", "+dtc+")")
    result = {"datos":eventos_schema.dump(event)}
    socketio.emit('my response', result)

@socketio.on('check')
def check_event():
    socketio.emit('response', True)

if __name__ == "__main__":
    socketio.run(app, debug=True)