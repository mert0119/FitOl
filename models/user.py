from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Profil bilgileri
    first_name = db.Column(db.String(50), default='')
    last_name = db.Column(db.String(50), default='')
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))  # 'erkek' veya 'kadin'
    height = db.Column(db.Float)  # cm
    weight = db.Column(db.Float)  # kg
    target_weight = db.Column(db.Float)  # kg
    activity_level = db.Column(db.String(20), default='orta')  # dusuk, orta, yuksek, cok_yuksek
    goal = db.Column(db.String(20), default='koruma')  # kilo_verme, kilo_alma, koruma
    daily_calorie_goal = db.Column(db.Integer, default=2000)
    daily_water_goal = db.Column(db.Float, default=2.5)  # litre
    protein_goal = db.Column(db.Integer, default=150)  # gram
    carbs_goal = db.Column(db.Integer, default=200)  # gram
    fat_goal = db.Column(db.Integer, default=65)  # gram
    profile_photo = db.Column(db.String(200), default='')  # dosya yolu

    # İlişkiler
    food_logs = db.relationship('FoodLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    water_logs = db.relationship('WaterLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    measurements = db.relationship('Measurement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    diet_plans = db.relationship('DietPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_bmr(self):
        """Bazal Metabolizma Hızı (Mifflin-St Jeor formülü)"""
        if not self.weight or not self.height or not self.age or not self.gender:
            return None
        if self.gender == 'erkek':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

    def calculate_tdee(self):
        """Günlük Toplam Enerji Harcaması"""
        bmr = self.calculate_bmr()
        if bmr is None:
            return None
        multipliers = {
            'dusuk': 1.2,
            'orta': 1.55,
            'yuksek': 1.725,
            'cok_yuksek': 1.9
        }
        return bmr * multipliers.get(self.activity_level, 1.55)

    def calculate_bmi(self):
        """Vücut Kitle İndeksi"""
        if not self.weight or not self.height:
            return None
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 1)

    def get_bmi_category(self):
        """BMI kategorisi"""
        bmi = self.calculate_bmi()
        if bmi is None:
            return None
        if bmi < 18.5:
            return 'Zayıf'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Fazla Kilolu'
        else:
            return 'Obez'

    def __repr__(self):
        return f'<User {self.username}>'
