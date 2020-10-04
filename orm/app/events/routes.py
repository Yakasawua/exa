from . import event_bp

from app.events.functions import list_event, event, update_event


@event_bp.route('/event/add', methods=['POST'])
def event_():
    return event()

@event_bp.route('/event/update', methods=['PUT'])
def update_():
    return update_event()

@event_bp.route('/list', methods=['POST'])
def list_():
    return list_event()
    