from datetime import datetime
from models import db


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(300), default='')
    reminder_time = db.Column(db.String(5), nullable=False)  # "08:30" HH:MM
    repeat_type = db.Column(db.String(20), default='daily')  # daily, weekdays, custom
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('reminders', lazy='dynamic'))

    def __repr__(self):
        return f'<Reminder {self.title} at {self.reminder_time}>'
