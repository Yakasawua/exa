from flask import Flask, jsonify, request, json, Response, render_template
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from werkzeug.utils import secure_filename
import json
#from models import Img
app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'palafox88'
app.config['MYSQL_DB'] = 'exa'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'secret'

mysql = MySQL(app)
bcryp = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app)

def write_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


@app.route('/users/register', methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password = bcryp.generate_password_hash(request.get_json()['password']).decode('utf-8')
    created = datetime.utcnow()

    cur.execute("INSERT INTO users (first_name, last_name, email, password, created) VALUES ('"+
    str(first_name) + "','" +
    str(last_name) + "','" +
    str(email) + "','" +
    str(password) + "','" +
    str(created) + "')")
    
    mysql.connection.commit()

    result = {
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email,
        "password" : password,
        "created" : created
    }

    return jsonify({"result": result})

@app.route('/users/login', methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    email = request.get_json()['email']
    password = request.get_json()['password']
    result = ""

    cur.execute("SELECT * FROM users where email = '" + str(email)+ "'")
    rv = cur.fetchone()

    if bcryp.check_password_hash(rv['password'], password):
        access_token = create_access_token(identity = {'id': rv['id'],'first_name': rv['first_name'], 'last_name': rv['last_name'], 'email': rv['email']})
        result = jsonify({"token":access_token})
    else:
        result = jsonify({"error":"email o contraseña invalidos"})
    #payload = decode_token(access_token)
    #str(payload['identity']['id'])
    return result


@app.route('/users', methods=['GET'])
def user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    rv = cur.fetchall()
    
    return jsonify(rv)


@app.route('/edit/<id>', methods=['POST'])
def edit_user(id):
    cur = mysql.connection.cursor()
    first_name = "test"
    last_name = "test"
    cur.execute("UPDATE users SET first_name = %s, last_name = %s WHERE id = %s", (first_name, last_name, id))
    
    mysql.connection.commit()

    result = {
        "first_name" : first_name,
        "last_name" : last_name
    }

    return jsonify({"result": result})



def upload(pic):
    print (pic)
    if not pic:
        return 'No pic uploaded', 400

    filename = secure_filename(pic.filename)
    img=pic.read()
    mimetype = pic.mimetype
    
    #img = Img(img=pic.read(), mimetype=mimetype, name=filename)
    cur = mysql.connection.cursor()

    sql_insert_blob_query = """ INSERT INTO picture (img, name, mimetype) VALUES (%s,%s,%s)"""
    insert_blob_tuple = (img, filename, mimetype)
    result = cur.execute(sql_insert_blob_query, insert_blob_tuple)

    #cur.execute("INSERT INTO img (img, name) VALUES ('"+
    #img + "','" +
    #filename + "')")
    ids = mysql.connection.insert_id()
    print (ids)
    mysql.connection.commit()
    
    return (ids)

@app.route('/picture/<id>', methods=['GET'])
def readpicture(id):
    cur = mysql.connection.cursor()
    sql_fetch_blob_query = """SELECT * from picture where id = %s"""
    
    cur.execute(sql_fetch_blob_query, (id,))
    rv = cur.fetchall()
    print (rv[0]['name'])
    for row in rv:
        #print("Id = ", row)
        image = row
      #  print("Name = ", row[2])
      #  image = row[1]
      #  photo = "C:\\Users\\Yakasawua\\Documents\\prueba\\algo.png"
      #  write_file(image, photo)
    return Response(rv[0]['img'], mimetype=rv[0]['mimetype'])
#point sql: INSERT INTO t1 (pt_col) VALUES(Point(1,2));

@app.route('/date', methods=['POST'])
def date():
    t = datetime(2020,8,13,4,50,34)
    created = datetime.utcnow()
    print (t)
    print (created)
    return (str(t) + ' otra: ' + str(created))

@app.route('/event/edit', methods=['POST'])
def edit_event():
    pic = request.files['pic']
    token = request.form['token']
    payload = decode_token(token)
    id_user = str(payload['identity']['id'])
    _id = request.form['_id']
    cur = mysql.connection.cursor()
    event_name ='modificado'
    descrip = 'dess'
    coorx = 34.4352
    coory = 76.2458
    img = upload(pic)
    date = datetime(2020,8,13,4,50,30)

    cur.execute("UPDATE eventos SET event_name = %s, descrip = %s, coor = Point(%s,%s), id_img = %s, date = %s, id_user = %s WHERE (id = %s)", (event_name, descrip, coorx,coory,img,date,id_user,_id))
    mysql.connection.commit()
    check_event()
    return ('evento actualizado')

@app.route('/event', methods=['POST'])
def event():
    pic = request.files['pic']

    token = request.form['token']
    payload = decode_token(token)
    id_user = str(payload['identity']['id'])
    cur = mysql.connection.cursor()
    event_name ='nombre'
    descrip = 'descripcion'
    coorx = 34
    coory = 76
    img = upload(pic)
    date = datetime(2020,8,13,4,50,34)

    cur.execute("INSERT INTO eventos (event_name, descrip, id_img, date, id_user) VALUES ('"+
    str(event_name) + "','" +
    str(descrip) + "','" +
    str(img) + "','" +
    str(date) + "','" +
    str(id_user) + "')")
    ids = mysql.connection.insert_id()
    mysql.connection.commit()
    cur.execute("UPDATE eventos SET coor = Point(%s,%s) WHERE id=%s",(coorx,coory,ids))
    mysql.connection.commit()
    check_event()
    return (str(event_name) + "," +
    str(descrip) + "," +
    str(coorx) + "," +
    str(coory) + "," +
    str(img) + "," +    
    str(date) + "," +
    str(id_user) )

@app.route('/list', methods=['POST'])
def list_event():
    cur = mysql.connection.cursor()
    event_name = request.get_json()['event_name']
    date = request.get_json()['date']
    lat = request.get_json()['lat']
    lng = request.get_json()['lng']
    dtc = request.get_json()['dtc']
    id_user = request.get_json()['id_user']
    _id = request.get_json()['_id']
    #lat = "4.6097100"
    #lng = "-74.0817500"
    #dtc = "10921"
    sql_select_query = ""
    if event_name:
        sql_select_query = " SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM eventos where event_name = '"+event_name+"'"
    elif date: 
        sql_select_query = " SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM eventos where date = '"+date+"'"
    elif lat and lng and dtc:
        sql_select_query =  "SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM exa.eventos WHERE (acos(sin(radians("+lat+")) * sin(radians(ST_X(coor))) + cos(radians("+lat+")) * cos(radians(ST_X(coor))) * cos(radians("+lng+") - radians(ST_Y(coor)))) * 6378) >= "+dtc+" "
    elif id_user:
        sql_select_query = " SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM eventos where id_user = '"+id_user+"'"
    elif _id:
        sql_select_query = " SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM eventos where id = '"+_id+"'"
    #cur.execute("SELECT event_name,descrip, ST_AsText(coor),id_img,date FROM eventos where event_name = 'nombre'")
    cur.execute(sql_select_query)
    rv = cur.fetchall()
    print (rv)
    return jsonify(rv)
        
@app.route('/')
def index():
    return render_template( './AppPage.html' )

@socketio.on('my event')
def handle_event(json):
    cur = mysql.connection.cursor()
    lat = json['lat']
    lng = json['lng']
    dtc = json['dtc']
    #sql_select_query =  "SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM eventos"
    sql_select_query =  "SELECT event_name,descrip, ST_AsText(coor),id_img,date,id_user FROM exa.eventos WHERE (acos(sin(radians("+lat+")) * sin(radians(ST_X(coor))) + cos(radians("+lat+")) * cos(radians(ST_X(coor))) * cos(radians("+lng+") - radians(ST_Y(coor)))) * 6378) >= "+dtc+""
    cur.execute(sql_select_query)
    rv = cur.fetchall()
    print('Se agrego/modifico algo')
    print(rv)
    result = {"datos":rv}
    socketio.emit('my response', result)

@socketio.on('check')
def check_event():
    socketio.emit('response', True)
    
if __name__ == "__main__":
    socketio.run(app ,debug=True)

            