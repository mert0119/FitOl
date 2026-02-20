from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import func
from models import db
from models.food_log import FoodLog
from models.exercise_log import ExerciseLog
from models.water_log import WaterLog
from models.measurement import Measurement

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()

    # Günlük kalori toplamı
    daily_calories = db.session.query(
        func.coalesce(func.sum(FoodLog.calories), 0)
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.date == today
    ).scalar()

    # Günlük makro toplamları
    daily_macros = db.session.query(
        func.coalesce(func.sum(FoodLog.protein), 0),
        func.coalesce(func.sum(FoodLog.carbs), 0),
        func.coalesce(func.sum(FoodLog.fat), 0)
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.date == today
    ).first()

    # Günlük su toplamı (ml -> litre)
    daily_water_ml = db.session.query(
        func.coalesce(func.sum(WaterLog.amount_ml), 0)
    ).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.date == today
    ).scalar()

    # Günlük egzersiz toplamı
    daily_exercise = db.session.query(
        func.coalesce(func.sum(ExerciseLog.calories_burned), 0),
        func.coalesce(func.sum(ExerciseLog.duration), 0)
    ).filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.date == today
    ).first()

    # Son 7 gün kalori verisi (grafik için)
    weekly_calories = []
    weekly_labels = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        cal = db.session.query(
            func.coalesce(func.sum(FoodLog.calories), 0)
        ).filter(
            FoodLog.user_id == current_user.id,
            FoodLog.date == d
        ).scalar()
        weekly_calories.append(round(cal))
        weekly_labels.append(d.strftime('%d/%m'))

    # Son ölçüm
    last_measurement = Measurement.query.filter_by(
        user_id=current_user.id
    ).order_by(Measurement.date.desc()).first()

    # Motivasyon mesajları
    import random
    motivations = [
        "Bugün de harika gidiyorsun! 💪",
        "Her adım seni hedefe yaklaştırıyor! 🎯",
        "Disiplin, başarının anahtarıdır! 🔑",
        "Vücudun sana teşekkür edecek! 🌟",
        "Vazgeçme, en iyi versiyonun olmak üzeresin! 🚀",
        "Sağlıklı yaşam bir tercih değil, bir yaşam biçimi! 🍀",
        "Bugünün emeği, yarının gücü! ⚡",
        "Kendine yatırım yap, karşılığını alacaksın! 💎",
    ]

    return render_template('dashboard.html',
                           daily_calories=round(daily_calories),
                           daily_protein=round(daily_macros[0]),
                           daily_carbs=round(daily_macros[1]),
                           daily_fat=round(daily_macros[2]),
                           daily_water_ml=round(daily_water_ml),
                           daily_water_litre=round(daily_water_ml / 1000, 1),
                           daily_exercise_cal=round(daily_exercise[0]),
                           daily_exercise_min=round(daily_exercise[1]),
                           weekly_calories=weekly_calories,
                           weekly_labels=weekly_labels,
                           last_measurement=last_measurement,
                           motivation=random.choice(motivations),
                           today=today)
