from db import db
from static import EventType , EventStatus
from sqlalchemy import Enum

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    type = db.Column(db.Enum(EventType), nullable=False)
    status = db.Column(db.Enum(EventStatus), nullable=False)
    scheduled_start = db.Column(db.DateTime, nullable=False)
    actual_start = db.Column(db.DateTime)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    selections = db.relationship('Selection', backref='event', lazy=True)


