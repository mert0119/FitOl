import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('/profile')
@login_required
def view():
    return render_template('profile.html')


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.age = int(request.form.get('age', 0)) or None
        current_user.gender = request.form.get('gender', '')
        current_user.height = float(request.form.get('height', 0)) or None
        current_user.weight = float(request.form.get('weight', 0)) or None
        current_user.target_weight = float(request.form.get('target_weight', 0)) or None
        current_user.activity_level = request.form.get('activity_level', 'orta')
        current_user.goal = request.form.get('goal', 'koruma')

        # Makro hedefleri
        current_user.protein_goal = int(request.form.get('protein_goal', 150)) or 150
        current_user.carbs_goal = int(request.form.get('carbs_goal', 200)) or 200
        current_user.fat_goal = int(request.form.get('fat_goal', 65)) or 65

        # Profil fotoğrafı
        photo = request.files.get('profile_photo')
        if photo and photo.filename and allowed_file(photo.filename):
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"user_{current_user.id}.{photo.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(upload_dir, filename)
            photo.save(filepath)
            current_user.profile_photo = f"uploads/avatars/{filename}"

        # TDEE'den günlük kalori hedefini hesapla
        tdee = current_user.calculate_tdee()
        if tdee:
            if current_user.goal == 'kilo_verme':
                current_user.daily_calorie_goal = int(tdee - 500)
            elif current_user.goal == 'kilo_alma':
                current_user.daily_calorie_goal = int(tdee + 500)
            else:
                current_user.daily_calorie_goal = int(tdee)

        # Su hedefini hesapla (kg * 35ml)
        if current_user.weight:
            current_user.daily_water_goal = round(current_user.weight * 0.035, 1)

        db.session.commit()
        flash('Profil güncellendi! ✅', 'success')
        return redirect(url_for('profile.view'))

    return render_template('profile_edit.html')
