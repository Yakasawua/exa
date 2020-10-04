from app import socketio
from app.events.functions import handle, check_event

@socketio.on('my event')
def handle_event(json):
    handle(json)
    

@socketio.on('check')
def check_():
    check_event()