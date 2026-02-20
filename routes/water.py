from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from models import db
from models.water_log import WaterLog

water_bp = Blueprint('water', __name__)


@water_bp.route('/water')
@login_required
def index():
    today = date.today()
    selected_date = request.args.get('date', today.isoformat())
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = today

    logs = WaterLog.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).order_by(WaterLog.created_at.desc()).all()

    total_ml = db.session.query(
        func.coalesce(func.sum(WaterLog.amount_ml), 0)
    ).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.date == selected_date
    ).scalar()

    goal_ml = current_user.daily_water_goal * 1000
    percentage = min(round((total_ml / goal_ml) * 100), 100) if goal_ml > 0 else 0

    return render_template('water.html',
                           logs=logs,
                           total_ml=round(total_ml),
                           total_litre=round(total_ml / 1000, 1),
                           goal_ml=round(goal_ml),
                           goal_litre=current_user.daily_water_goal,
                           percentage=percentage,
                           selected_date=selected_date,
                           today=today)


@water_bp.route('/water/add', methods=['POST'])
@login_required
def add():
    amount_type = request.form.get('amount_type', 'glass')
    log_date = request.form.get('date', date.today().isoformat())

    try:
        log_date = date.fromisoformat(log_date)
    except ValueError:
        log_date = date.today()

    amounts = {
        'glass': 200,       # 1 bardak = 200ml
        'bottle_small': 500,  # küçük şişe
        'bottle_large': 1000, # büyük şişe
        'custom': float(request.form.get('amount_ml', 200))
    }

    amount_ml = amounts.get(amount_type, 200)

    entry = WaterLog(
        user_id=current_user.id,
        date=log_date,
        amount_ml=amount_ml
    )
    db.session.add(entry)
    db.session.commit()
    flash(f'{int(amount_ml)}ml su eklendi! 💧', 'success')
    return redirect(url_for('water.index', date=log_date.isoformat()))


@water_bp.route('/water/delete/<int:id>')
@login_required
def delete(id):
    entry = WaterLog.query.get_or_404(id)
    if entry.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('water.index'))

    log_date = entry.date.isoformat()
    db.session.delete(entry)
    db.session.commit()
    flash('Kayıt silindi.', 'info')
    return redirect(url_for('water.index', date=log_date))
