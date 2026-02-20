from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash('Başarıyla giriş yaptınız! 🎉', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('E-posta veya şifre hatalı.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        # Doğrulama
        if not username or not email or not password:
            flash('Tüm alanları doldurun.', 'error')
        elif password != password2:
            flash('Şifreler eşleşmiyor.', 'error')
        elif len(password) < 6:
            flash('Şifre en az 6 karakter olmalı.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten alınmış.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Hesabınız oluşturuldu! Profilinizi tamamlayın. 🎉', 'success')
            return redirect(url_for('profile.edit'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('auth.login'))
