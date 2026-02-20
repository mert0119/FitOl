from datetime import datetime, date
from models import db


class ExerciseLog(db.Model):
    __tablename__ = 'exercise_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    exercise_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # gogus, sirt, bacak, omuz, kol, kardiyo, esneklik
    duration = db.Column(db.Integer, default=0)  # dakika
    sets = db.Column(db.Integer, default=0)
    reps = db.Column(db.Integer, default=0)
    weight_kg = db.Column(db.Float, default=0)
    incline = db.Column(db.Float, default=0)  # kardiyo eğim %
    speed = db.Column(db.Float, default=0)  # kardiyo hız km/h
    calories_burned = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExerciseLog {self.exercise_name}>'
