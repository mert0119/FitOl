from datetime import datetime
from models import db


class DietPlan(db.Model):
    __tablename__ = 'diet_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.String(20))  # kilo_verme, kilo_alma, koruma
    daily_calories = db.Column(db.Integer)
    protein_ratio = db.Column(db.Float, default=30)  # yüzde
    carb_ratio = db.Column(db.Float, default=40)  # yüzde
    fat_ratio = db.Column(db.Float, default=30)  # yüzde
    breakfast = db.Column(db.Text, default='')
    lunch = db.Column(db.Text, default='')
    dinner = db.Column(db.Text, default='')
    snacks = db.Column(db.Text, default='')
    notes = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def protein_grams(self):
        if self.daily_calories:
            return round((self.daily_calories * self.protein_ratio / 100) / 4)
        return 0

    def carb_grams(self):
        if self.daily_calories:
            return round((self.daily_calories * self.carb_ratio / 100) / 4)
        return 0

    def fat_grams(self):
        if self.daily_calories:
            return round((self.daily_calories * self.fat_ratio / 100) / 9)
        return 0

    def __repr__(self):
        return f'<DietPlan {self.name}>'
