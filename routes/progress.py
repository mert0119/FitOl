import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import date
from models import db
from models.progress_photo import ProgressPhoto

progress_bp = Blueprint('progress', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@progress_bp.route('/progress')
@login_required
def index():
    photos = ProgressPhoto.query.filter_by(user_id=current_user.id) \
        .order_by(ProgressPhoto.date.desc()).all()
    return render_template('progress/index.html', photos=photos)


@progress_bp.route('/progress/add', methods=['POST'])
@login_required
def add():
    photo_file = request.files.get('photo')
    weight = request.form.get('weight', '')
    notes = request.form.get('notes', '').strip()
    photo_date = request.form.get('date', date.today().isoformat())

    try:
        photo_date = date.fromisoformat(photo_date)
    except ValueError:
        photo_date = date.today()

    if not photo_file or not photo_file.filename:
        flash('Lütfen bir fotoğraf seçin.', 'error')
        return redirect(url_for('progress.index'))

    if not allowed_file(photo_file.filename):
        flash('Desteklenmeyen dosya formatı. PNG, JPG, WEBP kullanın.', 'error')
        return redirect(url_for('progress.index'))

    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'progress')
    os.makedirs(upload_dir, exist_ok=True)

    ext = photo_file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{current_user.id}_{photo_date.isoformat()}_{os.urandom(4).hex()}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    photo_file.save(filepath)

    try:
        weight_val = float(weight.replace(',', '.')) if weight else None
    except ValueError:
        weight_val = None

    entry = ProgressPhoto(
        user_id=current_user.id,
        date=photo_date,
        photo_path=f"uploads/progress/{filename}",
        weight=weight_val,
        notes=notes
    )
    db.session.add(entry)
    db.session.commit()
    flash('İlerleme fotoğrafı eklendi! 📸', 'success')
    return redirect(url_for('progress.index'))


@progress_bp.route('/progress/delete/<int:id>')
@login_required
def delete(id):
    photo = ProgressPhoto.query.get_or_404(id)
    if photo.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('progress.index'))

    # Dosyayı sil
    filepath = os.path.join(current_app.root_path, 'static', photo.photo_path)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()
    flash('Fotoğraf silindi.', 'info')
    return redirect(url_for('progress.index'))
