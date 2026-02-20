from datetime import datetime, date
from models import db


class WaterLog(db.Model):
    __tablename__ = 'water_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    amount_ml = db.Column(db.Float, nullable=False)  # mililitre
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WaterLog {self.amount_ml}ml>'
