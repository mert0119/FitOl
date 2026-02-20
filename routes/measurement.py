from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import func
from models import db
from models.measurement import Measurement

measurement_bp = Blueprint('measurement', __name__)


@measurement_bp.route('/measurement')
@login_required
def log():
    measurements = Measurement.query.filter_by(
        user_id=current_user.id
    ).order_by(Measurement.date.desc()).limit(30).all()

    return render_template('measurement/log.html', measurements=measurements)


@measurement_bp.route('/measurement/add', methods=['POST'])
@login_required
def add():
    log_date = request.form.get('date', date.today().isoformat())
    try:
        log_date = date.fromisoformat(log_date)
    except ValueError:
        log_date = date.today()

    entry = Measurement(
        user_id=current_user.id,
        date=log_date,
        weight=float(request.form.get('weight', 0)) or None,
        waist=float(request.form.get('waist', 0)) or None,
        chest=float(request.form.get('chest', 0)) or None,
        arm=float(request.form.get('arm', 0)) or None,
        leg=float(request.form.get('leg', 0)) or None,
        hip=float(request.form.get('hip', 0)) or None,
        body_fat=float(request.form.get('body_fat', 0)) or None,
        notes=request.form.get('notes', '').strip()
    )
    db.session.add(entry)
    db.session.commit()

    # Profildeki kiloyu da güncelle
    if entry.weight:
        current_user.weight = entry.weight
        db.session.commit()

    flash('Ölçüm kaydedildi! 📏', 'success')
    return redirect(url_for('measurement.log'))


@measurement_bp.route('/measurement/delete/<int:id>')
@login_required
def delete(id):
    entry = Measurement.query.get_or_404(id)
    if entry.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('measurement.log'))

    db.session.delete(entry)
    db.session.commit()
    flash('Kayıt silindi.', 'info')
    return redirect(url_for('measurement.log'))


@measurement_bp.route('/measurement/chart')
@login_required
def chart():
    return render_template('measurement/chart.html')


@measurement_bp.route('/measurement/chart-data')
@login_required
def chart_data():
    """Grafik için JSON veri döndür"""
    days = request.args.get('days', 90, type=int)
    start_date = date.today() - timedelta(days=days)

    measurements = Measurement.query.filter(
        Measurement.user_id == current_user.id,
        Measurement.date >= start_date
    ).order_by(Measurement.date.asc()).all()

    data = {
        'labels': [],
        'weight': [],
        'waist': [],
        'chest': [],
        'arm': [],
        'leg': [],
        'hip': [],
        'body_fat': []
    }

    for m in measurements:
        data['labels'].append(m.date.strftime('%d/%m/%Y'))
        data['weight'].append(m.weight)
        data['waist'].append(m.waist)
        data['chest'].append(m.chest)
        data['arm'].append(m.arm)
        data['leg'].append(m.leg)
        data['hip'].append(m.hip)
        data['body_fat'].append(m.body_fat)

    return jsonify(data)
