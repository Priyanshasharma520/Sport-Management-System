from flask import  url_for ,current_app
from db import db

def activate_event(event):
    with current_app.test_client() as client:
        event_update_url = url_for("Event.activate_deactivate_event", event_id=event.id, _external=True)
        response = client.put(event_update_url, json={"active": True})
        if response.status_code == 201:
            event.active = True
            db.session.add(event)
            db.session.commit()

def deactivate_event(event):
    with current_app.test_client() as client:
        event_update_url = url_for("Event.activate_deactivate_event", event_id=event.id, _external=True)
        response = client.put(event_update_url, json={"active": False})
        if response.status_code == 201:
            event.active = False
            db.session.add(event)
            db.session.commit()

def update_sport_status(sport, new_status):
    with current_app.test_client() as client:
        sport_update_url = url_for("Sport.update_sport", sport_id=sport.id, _external=True)
        response = client.put(sport_update_url, json={"active": new_status})
        if response.status_code == 201:
            sport.active = new_status
            db.session.add(sport)
            db.session.commit()