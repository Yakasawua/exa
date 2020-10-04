from datetime import datetime
from sqlalchemy import func, Column
from sqlalchemy.types import UserDefinedType

from app import db, ma

class Point(UserDefinedType):
    def get_col_spec(self):
        return "POINT"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary(length=(2**32)-1), nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

class Eventos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(45), nullable=False)
    descrip = db.Column(db.String(500), nullable=False)
    coor =  Column(Point, nullable=False)
    id_img = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    id_user = db.Column(db.Integer, nullable=False)

class EventosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'event_name', 'descrip', 'coor', 'id_img', 'date', 'id_user')
