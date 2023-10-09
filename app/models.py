from datetime import datetime
from app import db


class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Double(12, 10))
    movement_type = db.Column(db.String(10))
    movement_date = db.Column(db.DateTime)
    register_date = db.Column(db.DateTime, default=datetime.now())
