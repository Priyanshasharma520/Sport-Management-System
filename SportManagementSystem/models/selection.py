from db import db
from static import SelectionOutcome
from sqlalchemy import Enum

class Selection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)  # Decimal with 2 decimal places
    active = db.Column(db.Boolean, default=True)
    outcome = db.Column(db.Enum(SelectionOutcome), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    # Define the unique constraint on name and event_id
    __table_args__ = (db.UniqueConstraint('name', 'event_id', name='uq_selection_name_event_id'),)