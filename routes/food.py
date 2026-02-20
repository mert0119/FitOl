from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import func
import json
import os
from models import db
from models.food_log import FoodLog

food_bp = Blueprint('food', __name__)

# Besin veritabanını yükle
FOODS_DB = []
foods_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'foods.json')
if os.path.exists(foods_path):
    with open(foods_path, 'r', encoding='utf-8') as f:
        FOODS_DB = json.load(f)


@food_bp.route('/food')
@login_required
def log():
    today = date.today()
    selected_date = request.args.get('date', today.isoformat())
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = today

    # Öğün bazlı kayıtlar
    meals = {}
    for meal_type in ['kahvalti', 'ogle', 'aksam', 'atistirmalik']:
        meals[meal_type] = FoodLog.query.filter_by(
            user_id=current_user.id,
            date=selected_date,
            meal_type=meal_type
        ).all()

    # Günlük toplamlar
    totals = db.session.query(
        func.coalesce(func.sum(FoodLog.calories), 0),
        func.coalesce(func.sum(FoodLog.protein), 0),
        func.coalesce(func.sum(FoodLog.carbs), 0),
        func.coalesce(func.sum(FoodLog.fat), 0)
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.date == selected_date
    ).first()

    meal_names = {
        'kahvalti': '🌅 Kahvaltı',
        'ogle': '☀️ Öğle Yemeği',
        'aksam': '🌙 Akşam Yemeği',
        'atistirmalik': '🍎 Atıştırmalık'
    }

    return render_template('food/log.html',
                           meals=meals,
                           meal_names=meal_names,
                           totals={
                               'calories': round(totals[0]),
                               'protein': round(totals[1]),
                               'carbs': round(totals[2]),
                               'fat': round(totals[3])
                           },
                           selected_date=selected_date,
                           today=today)


@food_bp.route('/food/add', methods=['POST'])
@login_required
def add():
    food_name = request.form.get('food_name', '').strip()
    meal_type = request.form.get('meal_type', 'kahvalti')
    portion = float(request.form.get('portion', 1))
    calories = float(request.form.get('calories', 0))
    protein = float(request.form.get('protein', 0))
    carbs = float(request.form.get('carbs', 0))
    fat = float(request.form.get('fat', 0))
    log_date = request.form.get('date', date.today().isoformat())

    try:
        log_date = date.fromisoformat(log_date)
    except ValueError:
        log_date = date.today()

    if not food_name:
        flash('Yemek adı gerekli.', 'error')
        return redirect(url_for('food.log'))

    entry = FoodLog(
        user_id=current_user.id,
        date=log_date,
        meal_type=meal_type,
        food_name=food_name,
        portion=portion,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat
    )
    db.session.add(entry)
    db.session.commit()
    flash(f'{food_name} eklendi! 🍽️', 'success')
    return redirect(url_for('food.log', date=log_date.isoformat()))


@food_bp.route('/food/delete/<int:id>')
@login_required
def delete(id):
    entry = FoodLog.query.get_or_404(id)
    if entry.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('food.log'))

    log_date = entry.date.isoformat()
    db.session.delete(entry)
    db.session.commit()
    flash('Kayıt silindi.', 'info')
    return redirect(url_for('food.log', date=log_date))


@food_bp.route('/food/search')
@login_required
def search():
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return jsonify([])

    results = [f for f in FOODS_DB if query in f['name'].lower()][:15]
    return jsonify(results)


@food_bp.route('/food/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    logs = FoodLog.query.filter_by(
        user_id=current_user.id
    ).order_by(FoodLog.date.desc(), FoodLog.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('food/history.html', logs=logs)
