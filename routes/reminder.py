from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db
from models.reminder import Reminder

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/reminders')
@login_required
def index():
    reminders = Reminder.query.filter_by(user_id=current_user.id) \
        .order_by(Reminder.reminder_time).all()
    return render_template('reminder/index.html', reminders=reminders)


@reminder_bp.route('/reminders/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    reminder_time = request.form.get('reminder_time', '08:00')
    repeat_type = request.form.get('repeat_type', 'daily')

    if not title:
        flash('Hatırlatıcı başlığı gerekli.', 'error')
        return redirect(url_for('reminder.index'))

    entry = Reminder(
        user_id=current_user.id,
        title=title,
        message=message,
        reminder_time=reminder_time,
        repeat_type=repeat_type
    )
    db.session.add(entry)
    db.session.commit()
    flash(f'Hatırlatıcı eklendi! 🔔 {reminder_time}', 'success')
    return redirect(url_for('reminder.index'))


@reminder_bp.route('/reminders/toggle/<int:id>')
@login_required
def toggle(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('reminder.index'))

    reminder.is_active = not reminder.is_active
    db.session.commit()
    status = "aktif" if reminder.is_active else "pasif"
    flash(f'Hatırlatıcı {status} yapıldı.', 'info')
    return redirect(url_for('reminder.index'))


@reminder_bp.route('/reminders/delete/<int:id>')
@login_required
def delete(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('reminder.index'))

    db.session.delete(reminder)
    db.session.commit()
    flash('Hatırlatıcı silindi.', 'info')
    return redirect(url_for('reminder.index'))


@reminder_bp.route('/reminders/check')
@login_required
def check():
    """AJAX: Şu anki saate denk gelen hatırlatıcıları döner"""
    now = datetime.now().strftime('%H:%M')
    active = Reminder.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        reminder_time=now
    ).all()

    return jsonify([{
        'id': r.id,
        'title': r.title,
        'message': r.message,
        'time': r.reminder_time
    } for r in active])
