from datetime import datetime, date
from models import db


class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    weight = db.Column(db.Float)  # kg
    waist = db.Column(db.Float)  # cm - bel
    chest = db.Column(db.Float)  # cm - göğüs
    arm = db.Column(db.Float)  # cm - kol
    leg = db.Column(db.Float)  # cm - bacak
    hip = db.Column(db.Float)  # cm - kalça
    body_fat = db.Column(db.Float)  # yüzde
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Measurement {self.date} - {self.weight}kg>'
