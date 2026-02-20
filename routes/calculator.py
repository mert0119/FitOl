from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

calculator_bp = Blueprint('calculator', __name__)


@calculator_bp.route('/calculator', methods=['GET', 'POST'])
@login_required
def index():
    results = None

    if request.method == 'POST':
        try:
            weight = float(request.form.get('weight', 0))
            height = float(request.form.get('height', 0))
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', 'erkek')
            activity_level = request.form.get('activity_level', 'orta')

            if weight <= 0 or height <= 0 or age <= 0:
                results = {'error': 'Lütfen geçerli değerler girin.'}
            else:
                # BMI
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 1)

                if bmi < 18.5:
                    bmi_category = 'Zayıf'
                    bmi_color = '#3498db'
                elif bmi < 25:
                    bmi_category = 'Normal'
                    bmi_color = '#2ecc71'
                elif bmi < 30:
                    bmi_category = 'Fazla Kilolu'
                    bmi_color = '#f39c12'
                else:
                    bmi_category = 'Obez'
                    bmi_color = '#e74c3c'

                # BMR (Mifflin-St Jeor)
                if gender == 'erkek':
                    bmr = 10 * weight + 6.25 * height - 5 * age + 5
                else:
                    bmr = 10 * weight + 6.25 * height - 5 * age - 161

                # TDEE
                multipliers = {
                    'dusuk': 1.2,
                    'orta': 1.55,
                    'yuksek': 1.725,
                    'cok_yuksek': 1.9
                }
                tdee = bmr * multipliers.get(activity_level, 1.55)

                # İdeal kilo (Devine formülü)
                if gender == 'erkek':
                    ideal_weight = 50 + 2.3 * ((height / 2.54) - 60)
                else:
                    ideal_weight = 45.5 + 2.3 * ((height / 2.54) - 60)

                # Vücut yağ oranı tahmini (US Navy yöntemi yaklaşık)
                if gender == 'erkek':
                    body_fat = round(1.2 * bmi + 0.23 * age - 16.2, 1)
                else:
                    body_fat = round(1.2 * bmi + 0.23 * age - 5.4, 1)

                results = {
                    'bmi': bmi,
                    'bmi_category': bmi_category,
                    'bmi_color': bmi_color,
                    'bmr': round(bmr),
                    'tdee': round(tdee),
                    'ideal_weight': round(ideal_weight, 1),
                    'body_fat': max(body_fat, 5),
                    'calories_lose': round(tdee - 500),
                    'calories_gain': round(tdee + 500),
                    'calories_maintain': round(tdee),
                    'weight': weight,
                    'height': height,
                    'age': age,
                    'gender': gender,
                    'activity_level': activity_level
                }
        except (ValueError, TypeError):
            results = {'error': 'Lütfen geçerli sayısal değerler girin.'}

    # Profil bilgilerini varsayılan olarak doldur
    defaults = {
        'weight': current_user.weight or '',
        'height': current_user.height or '',
        'age': current_user.age or '',
        'gender': current_user.gender or 'erkek',
        'activity_level': current_user.activity_level or 'orta'
    }

    return render_template('calculator.html', results=results, defaults=defaults)
