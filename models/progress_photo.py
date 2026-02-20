from datetime import datetime, date
from models import db


class ProgressPhoto(db.Model):
    __tablename__ = 'progress_photos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    photo_path = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float)  # o günkü kilo
    notes = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('progress_photos', lazy='dynamic'))

    def __repr__(self):
        return f'<ProgressPhoto {self.date}>'
