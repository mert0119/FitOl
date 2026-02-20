from datetime import datetime, date
from models import db


class FoodLog(db.Model):
    __tablename__ = 'food_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    meal_type = db.Column(db.String(20), nullable=False)  # kahvalti, ogle, aksam, atistirmalik
    food_name = db.Column(db.String(200), nullable=False)
    portion = db.Column(db.Float, default=1.0)  # porsiyon miktarı
    portion_unit = db.Column(db.String(20), default='porsiyon')  # porsiyon, gram, adet
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)  # gram
    carbs = db.Column(db.Float, default=0)  # gram
    fat = db.Column(db.Float, default=0)  # gram
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FoodLog {self.food_name} - {self.calories} kcal>'
