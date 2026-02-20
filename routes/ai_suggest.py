import json
import os
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from models import db
from models.food_log import FoodLog

ai_suggest_bp = Blueprint('ai_suggest', __name__)


def load_foods():
    foods_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'foods.json')
    with open(foods_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@ai_suggest_bp.route('/food/suggest')
@login_required
def suggest():
    today = date.today()

    # Bugün tüketilen toplam makrolar
    consumed = db.session.query(
        func.coalesce(func.sum(FoodLog.calories), 0),
        func.coalesce(func.sum(FoodLog.protein), 0),
        func.coalesce(func.sum(FoodLog.carbs), 0),
        func.coalesce(func.sum(FoodLog.fat), 0)
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.date == today
    ).first()

    consumed_cal = float(consumed[0])
    consumed_protein = float(consumed[1])
    consumed_carbs = float(consumed[2])
    consumed_fat = float(consumed[3])

    # Hedefler
    cal_goal = current_user.daily_calorie_goal or 2000
    protein_goal = current_user.protein_goal or 150
    carbs_goal = current_user.carbs_goal or 200
    fat_goal = current_user.fat_goal or 65

    remaining = {
        'calories': max(0, cal_goal - consumed_cal),
        'protein': max(0, protein_goal - consumed_protein),
        'carbs': max(0, carbs_goal - consumed_carbs),
        'fat': max(0, fat_goal - consumed_fat)
    }

    # Hangi makro en çok geride?
    protein_ratio = consumed_protein / max(protein_goal, 1)
    carbs_ratio = consumed_carbs / max(carbs_goal, 1)
    fat_ratio = consumed_fat / max(fat_goal, 1)

    if protein_ratio <= carbs_ratio and protein_ratio <= fat_ratio:
        priority = 'protein'
        priority_label = 'Protein'
    elif carbs_ratio <= fat_ratio:
        priority = 'carbs'
        priority_label = 'Karbonhidrat'
    else:
        priority = 'fat'
        priority_label = 'Yağ'

    # foods.json'dan filtreleme
    all_foods = load_foods()
    suggestions = []

    for food in all_foods:
        cal = food.get('cal', 0)
        protein = food.get('protein', 0)
        carbs = food.get('carbs', 0)
        fat = food.get('fat', 0)

        # Kalan kaloriye sığacak yemekler (en fazla kalanın %80'i)
        if cal > remaining['calories'] * 0.8 and remaining['calories'] > 100:
            continue

        # Öncelikli makroya göre skor hesapla
        if priority == 'protein':
            score = protein * 3 - fat * 0.5
        elif priority == 'carbs':
            score = carbs * 2 + protein
        else:
            score = fat * 2 + protein

        if score > 0:
            suggestions.append({
                'name': food['name'],
                'cal': cal,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'score': round(score, 1),
                'category': food.get('category', '')
            })

    # En iyi 12 öneri
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    suggestions = suggestions[:12]

    return render_template('food/suggest.html',
                           consumed={
                               'calories': round(consumed_cal),
                               'protein': round(consumed_protein),
                               'carbs': round(consumed_carbs),
                               'fat': round(consumed_fat)
                           },
                           goals={
                               'calories': cal_goal,
                               'protein': protein_goal,
                               'carbs': carbs_goal,
                               'fat': fat_goal
                           },
                           remaining=remaining,
                           priority=priority,
                           priority_label=priority_label,
                           suggestions=suggestions)
