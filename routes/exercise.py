from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from models import db
from models.exercise_log import ExerciseLog

exercise_bp = Blueprint('exercise', __name__)

# Hazır egzersiz kütüphanesi
EXERCISES = {
    'gogus': [
        {'name': 'Bench Press', 'cal_per_min': 8},
        {'name': 'Dumbbell Press', 'cal_per_min': 7},
        {'name': 'Şınav', 'cal_per_min': 7},
        {'name': 'Cable Crossover', 'cal_per_min': 6},
        {'name': 'İncline Press', 'cal_per_min': 8},
        {'name': 'Decline Press', 'cal_per_min': 8},
        {'name': 'Dips', 'cal_per_min': 8},
        {'name': 'İncline Dumbbell Press', 'cal_per_min': 7},
        {'name': 'Dumbbell Fly', 'cal_per_min': 6},
        {'name': 'İncline Dumbbell Fly', 'cal_per_min': 6},
        {'name': 'Pec Deck', 'cal_per_min': 5},
        {'name': 'Machine Chest Press', 'cal_per_min': 6},
        {'name': 'Landmine Press', 'cal_per_min': 7},
        {'name': 'Svend Press', 'cal_per_min': 5},
        {'name': 'Push-Up (Geniş Tutuş)', 'cal_per_min': 7},
        {'name': 'Push-Up (Dar Tutuş)', 'cal_per_min': 7},
    ],
    'sirt': [
        {'name': 'Barfiks', 'cal_per_min': 9},
        {'name': 'Lat Pulldown', 'cal_per_min': 7},
        {'name': 'Barbell Row', 'cal_per_min': 8},
        {'name': 'Dumbbell Row', 'cal_per_min': 7},
        {'name': 'Cable Row', 'cal_per_min': 6},
        {'name': 'Deadlift', 'cal_per_min': 10},
        {'name': 'T-Bar Row', 'cal_per_min': 8},
        {'name': 'Seated Cable Row', 'cal_per_min': 6},
        {'name': 'Face Pull', 'cal_per_min': 5},
        {'name': 'Straight Arm Pulldown', 'cal_per_min': 5},
        {'name': 'Rack Pull', 'cal_per_min': 9},
        {'name': 'Pendlay Row', 'cal_per_min': 8},
        {'name': 'Meadows Row', 'cal_per_min': 7},
        {'name': 'Seal Row', 'cal_per_min': 7},
        {'name': 'Kayak Row (Makine)', 'cal_per_min': 6},
        {'name': 'Chin-Up', 'cal_per_min': 9},
        {'name': 'Inverted Row', 'cal_per_min': 6},
        {'name': 'Hyperextension', 'cal_per_min': 5},
    ],
    'bacak': [
        {'name': 'Squat', 'cal_per_min': 10},
        {'name': 'Leg Press', 'cal_per_min': 8},
        {'name': 'Leg Curl', 'cal_per_min': 6},
        {'name': 'Leg Extension', 'cal_per_min': 6},
        {'name': 'Lunge', 'cal_per_min': 9},
        {'name': 'Calf Raise', 'cal_per_min': 5},
        {'name': 'Front Squat', 'cal_per_min': 10},
        {'name': 'Bulgarian Split Squat', 'cal_per_min': 9},
        {'name': 'Romanian Deadlift', 'cal_per_min': 8},
        {'name': 'Sumo Deadlift', 'cal_per_min': 9},
        {'name': 'Hack Squat', 'cal_per_min': 8},
        {'name': 'Goblet Squat', 'cal_per_min': 8},
        {'name': 'Hip Thrust', 'cal_per_min': 7},
        {'name': 'Glute Bridge', 'cal_per_min': 6},
        {'name': 'Walking Lunge', 'cal_per_min': 9},
        {'name': 'Step-Up', 'cal_per_min': 7},
        {'name': 'Box Squat', 'cal_per_min': 9},
        {'name': 'Sissy Squat', 'cal_per_min': 6},
        {'name': 'Seated Calf Raise', 'cal_per_min': 4},
        {'name': 'Good Morning', 'cal_per_min': 7},
        {'name': 'Adductor (İç Bacak)', 'cal_per_min': 5},
        {'name': 'Abductor (Dış Bacak)', 'cal_per_min': 5},
    ],
    'omuz': [
        {'name': 'Military Press', 'cal_per_min': 7},
        {'name': 'Lateral Raise', 'cal_per_min': 5},
        {'name': 'Front Raise', 'cal_per_min': 5},
        {'name': 'Reverse Fly', 'cal_per_min': 5},
        {'name': 'Arnold Press', 'cal_per_min': 7},
        {'name': 'Shrug', 'cal_per_min': 5},
        {'name': 'Dumbbell Shoulder Press', 'cal_per_min': 7},
        {'name': 'Behind Neck Press', 'cal_per_min': 7},
        {'name': 'Cable Lateral Raise', 'cal_per_min': 5},
        {'name': 'Upright Row', 'cal_per_min': 6},
        {'name': 'Face Pull', 'cal_per_min': 5},
        {'name': 'Lu Raise', 'cal_per_min': 5},
        {'name': 'Rear Delt Fly (Makine)', 'cal_per_min': 5},
        {'name': 'Landmine Press (Omuz)', 'cal_per_min': 7},
        {'name': 'Bradford Press', 'cal_per_min': 7},
        {'name': 'Plate Front Raise', 'cal_per_min': 5},
    ],
    'kol': [
        {'name': 'Biceps Curl', 'cal_per_min': 5},
        {'name': 'Hammer Curl', 'cal_per_min': 5},
        {'name': 'Triceps Pushdown', 'cal_per_min': 5},
        {'name': 'Skull Crusher', 'cal_per_min': 6},
        {'name': 'Preacher Curl', 'cal_per_min': 5},
        {'name': 'Triceps Dips', 'cal_per_min': 7},
        {'name': 'Concentration Curl', 'cal_per_min': 4},
        {'name': 'EZ Bar Curl', 'cal_per_min': 5},
        {'name': 'Cable Curl', 'cal_per_min': 5},
        {'name': 'Overhead Triceps Extension', 'cal_per_min': 5},
        {'name': 'Close Grip Bench Press', 'cal_per_min': 7},
        {'name': 'Diamond Push-Up', 'cal_per_min': 7},
        {'name': 'Reverse Curl', 'cal_per_min': 5},
        {'name': 'Wrist Curl', 'cal_per_min': 3},
        {'name': 'Spider Curl', 'cal_per_min': 5},
        {'name': 'Incline Dumbbell Curl', 'cal_per_min': 5},
        {'name': 'Bayesian Curl', 'cal_per_min': 5},
        {'name': 'Kickback', 'cal_per_min': 4},
        {'name': 'Rope Pushdown', 'cal_per_min': 5},
    ],
    'karin': [
        {'name': 'Crunch', 'cal_per_min': 6},
        {'name': 'Plank', 'cal_per_min': 5},
        {'name': 'Bicycle Crunch', 'cal_per_min': 7},
        {'name': 'Leg Raise', 'cal_per_min': 6},
        {'name': 'Russian Twist', 'cal_per_min': 7},
        {'name': 'Mountain Climber', 'cal_per_min': 10},
        {'name': 'Ab Wheel Rollout', 'cal_per_min': 8},
        {'name': 'Hanging Leg Raise', 'cal_per_min': 7},
        {'name': 'Cable Crunch', 'cal_per_min': 6},
        {'name': 'Side Plank', 'cal_per_min': 4},
        {'name': 'V-Up', 'cal_per_min': 7},
        {'name': 'Flutter Kick', 'cal_per_min': 6},
        {'name': 'Dead Bug', 'cal_per_min': 5},
        {'name': 'Pallof Press', 'cal_per_min': 5},
    ],
    'kardiyo': [
        {'name': 'Koşu', 'cal_per_min': 12},
        {'name': 'Bisiklet', 'cal_per_min': 10},
        {'name': 'Yüzme', 'cal_per_min': 11},
        {'name': 'İp Atlama', 'cal_per_min': 13},
        {'name': 'Yürüyüş', 'cal_per_min': 5},
        {'name': 'HIIT', 'cal_per_min': 14},
        {'name': 'Merdiven Çıkma', 'cal_per_min': 9},
        {'name': 'Eliptik', 'cal_per_min': 8},
        {'name': 'Kürek Makinesi', 'cal_per_min': 10},
        {'name': 'Koşu Bandı', 'cal_per_min': 11},
        {'name': 'Stair Master', 'cal_per_min': 10},
        {'name': 'Sprint', 'cal_per_min': 16},
        {'name': 'Box Jump', 'cal_per_min': 12},
        {'name': 'Burpee', 'cal_per_min': 14},
        {'name': 'Battle Rope', 'cal_per_min': 13},
        {'name': 'Kettlebell Swing', 'cal_per_min': 12},
        {'name': 'Tabata', 'cal_per_min': 15},
        {'name': 'Assault Bike', 'cal_per_min': 14},
        {'name': 'Skiing Makinesi', 'cal_per_min': 11},
        {'name': 'Outdoor Bisiklet', 'cal_per_min': 10},
    ],
    'esneklik': [
        {'name': 'Yoga', 'cal_per_min': 4},
        {'name': 'Pilates', 'cal_per_min': 5},
        {'name': 'Stretching', 'cal_per_min': 3},
        {'name': 'Foam Rolling', 'cal_per_min': 3},
        {'name': 'Dinamik Isınma', 'cal_per_min': 5},
        {'name': 'Mobility Drill', 'cal_per_min': 4},
        {'name': 'Band Stretching', 'cal_per_min': 3},
        {'name': 'Soğuma (Cool Down)', 'cal_per_min': 3},
    ]
}

CATEGORY_NAMES = {
    'gogus': '🏋️ Göğüs',
    'sirt': '💪 Sırt',
    'bacak': '🦵 Bacak',
    'omuz': '🤸 Omuz',
    'kol': '💪 Kol',
    'karin': '🔥 Karın',
    'kardiyo': '🏃 Kardiyo',
    'esneklik': '🧘 Esneklik'
}

# Hazır antrenman programları
PROGRAMS = {
    'baslangic': {
        'name': '🌱 Başlangıç Programı',
        'description': 'Spora yeni başlayanlar için haftada 3 gün program',
        'days': {
            'Pazartesi': [
                {'exercise': 'Şınav', 'sets': 3, 'reps': 10},
                {'exercise': 'Squat', 'sets': 3, 'reps': 12},
                {'exercise': 'Dumbbell Row', 'sets': 3, 'reps': 10},
                {'exercise': 'Lateral Raise', 'sets': 3, 'reps': 12},
            ],
            'Çarşamba': [
                {'exercise': 'Bench Press', 'sets': 3, 'reps': 10},
                {'exercise': 'Leg Press', 'sets': 3, 'reps': 12},
                {'exercise': 'Lat Pulldown', 'sets': 3, 'reps': 10},
                {'exercise': 'Biceps Curl', 'sets': 3, 'reps': 12},
            ],
            'Cuma': [
                {'exercise': 'Dips', 'sets': 3, 'reps': 8},
                {'exercise': 'Lunge', 'sets': 3, 'reps': 10},
                {'exercise': 'Barbell Row', 'sets': 3, 'reps': 10},
                {'exercise': 'Triceps Pushdown', 'sets': 3, 'reps': 12},
            ],
        }
    },
    'orta': {
        'name': '⚡ Orta Seviye Programı',
        'description': '3-6 aylık deneyimi olanlar için haftada 4 gün bölünmüş program',
        'days': {
            'Pazartesi - Göğüs/Triceps': [
                {'exercise': 'Bench Press', 'sets': 4, 'reps': 10},
                {'exercise': 'İncline Press', 'sets': 3, 'reps': 10},
                {'exercise': 'Cable Crossover', 'sets': 3, 'reps': 12},
                {'exercise': 'Skull Crusher', 'sets': 3, 'reps': 12},
                {'exercise': 'Triceps Pushdown', 'sets': 3, 'reps': 12},
            ],
            'Salı - Sırt/Biceps': [
                {'exercise': 'Barfiks', 'sets': 4, 'reps': 8},
                {'exercise': 'Barbell Row', 'sets': 4, 'reps': 10},
                {'exercise': 'Cable Row', 'sets': 3, 'reps': 12},
                {'exercise': 'Biceps Curl', 'sets': 3, 'reps': 12},
                {'exercise': 'Hammer Curl', 'sets': 3, 'reps': 12},
            ],
            'Perşembe - Bacak': [
                {'exercise': 'Squat', 'sets': 4, 'reps': 10},
                {'exercise': 'Leg Press', 'sets': 3, 'reps': 12},
                {'exercise': 'Leg Curl', 'sets': 3, 'reps': 12},
                {'exercise': 'Leg Extension', 'sets': 3, 'reps': 12},
                {'exercise': 'Calf Raise', 'sets': 4, 'reps': 15},
            ],
            'Cuma - Omuz/Karın': [
                {'exercise': 'Military Press', 'sets': 4, 'reps': 10},
                {'exercise': 'Lateral Raise', 'sets': 3, 'reps': 12},
                {'exercise': 'Front Raise', 'sets': 3, 'reps': 12},
                {'exercise': 'Reverse Fly', 'sets': 3, 'reps': 12},
                {'exercise': 'Shrug', 'sets': 3, 'reps': 15},
            ],
        }
    },
    'ileri': {
        'name': '🔥 İleri Seviye Programı',
        'description': '1+ yıl deneyimi olanlar için haftada 5 gün yoğun program',
        'days': {
            'Pazartesi - Göğüs': [
                {'exercise': 'Bench Press', 'sets': 5, 'reps': 8},
                {'exercise': 'İncline Press', 'sets': 4, 'reps': 10},
                {'exercise': 'Dumbbell Press', 'sets': 4, 'reps': 10},
                {'exercise': 'Cable Crossover', 'sets': 3, 'reps': 12},
                {'exercise': 'Dips', 'sets': 3, 'reps': 12},
            ],
            'Salı - Sırt': [
                {'exercise': 'Deadlift', 'sets': 5, 'reps': 5},
                {'exercise': 'Barfiks', 'sets': 4, 'reps': 10},
                {'exercise': 'Barbell Row', 'sets': 4, 'reps': 10},
                {'exercise': 'Dumbbell Row', 'sets': 3, 'reps': 12},
                {'exercise': 'Lat Pulldown', 'sets': 3, 'reps': 12},
            ],
            'Çarşamba - Bacak': [
                {'exercise': 'Squat', 'sets': 5, 'reps': 8},
                {'exercise': 'Leg Press', 'sets': 4, 'reps': 12},
                {'exercise': 'Lunge', 'sets': 3, 'reps': 10},
                {'exercise': 'Leg Curl', 'sets': 4, 'reps': 12},
                {'exercise': 'Leg Extension', 'sets': 4, 'reps': 12},
                {'exercise': 'Calf Raise', 'sets': 5, 'reps': 15},
            ],
            'Perşembe - Omuz': [
                {'exercise': 'Military Press', 'sets': 5, 'reps': 8},
                {'exercise': 'Arnold Press', 'sets': 4, 'reps': 10},
                {'exercise': 'Lateral Raise', 'sets': 4, 'reps': 12},
                {'exercise': 'Reverse Fly', 'sets': 3, 'reps': 12},
                {'exercise': 'Shrug', 'sets': 4, 'reps': 12},
            ],
            'Cuma - Kol': [
                {'exercise': 'Biceps Curl', 'sets': 4, 'reps': 10},
                {'exercise': 'Hammer Curl', 'sets': 3, 'reps': 12},
                {'exercise': 'Preacher Curl', 'sets': 3, 'reps': 12},
                {'exercise': 'Skull Crusher', 'sets': 4, 'reps': 10},
                {'exercise': 'Triceps Pushdown', 'sets': 3, 'reps': 12},
                {'exercise': 'Triceps Dips', 'sets': 3, 'reps': 12},
            ],
        }
    }
}


@exercise_bp.route('/exercise')
@login_required
def log():
    today = date.today()
    selected_date = request.args.get('date', today.isoformat())
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = today

    logs = ExerciseLog.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).order_by(ExerciseLog.created_at.desc()).all()

    # Günlük toplam
    totals = db.session.query(
        func.coalesce(func.sum(ExerciseLog.calories_burned), 0),
        func.coalesce(func.sum(ExerciseLog.duration), 0)
    ).filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.date == selected_date
    ).first()

    return render_template('exercise/log.html',
                           logs=logs,
                           exercises=EXERCISES,
                           category_names=CATEGORY_NAMES,
                           total_calories=round(totals[0]),
                           total_duration=round(totals[1]),
                           selected_date=selected_date,
                           today=today)


@exercise_bp.route('/exercise/add', methods=['POST'])
@login_required
def add():
    exercise_name = request.form.get('exercise_name', '').strip()
    category = request.form.get('category', '')
    notes = request.form.get('notes', '').strip()
    log_date = request.form.get('date', date.today().isoformat())

    # Safe parsing — boş string crash etmesin
    def safe_int(val, default=0):
        try: return int(val) if val else default
        except (ValueError, TypeError): return default

    def safe_float(val, default=0.0):
        try: return float(str(val).replace(',', '.')) if val else default
        except (ValueError, TypeError): return default

    duration = safe_int(request.form.get('duration'))
    sets = safe_int(request.form.get('sets'))
    reps = safe_int(request.form.get('reps'))
    weight_kg = safe_float(request.form.get('weight_kg'))
    incline = safe_float(request.form.get('incline'))
    speed = safe_float(request.form.get('speed'))

    try:
        log_date = date.fromisoformat(log_date)
    except ValueError:
        log_date = date.today()

    if not exercise_name:
        flash('Egzersiz adı gerekli.', 'error')
        return redirect(url_for('exercise.log'))

    # Kalori hesapla
    cal_per_min = 7  # varsayılan
    for cat_exercises in EXERCISES.values():
        for ex in cat_exercises:
            if ex['name'] == exercise_name:
                cal_per_min = ex['cal_per_min']
                break

    is_cardio = category in ('kardiyo', 'esneklik')

    if is_cardio and duration > 0:
        # Kardiyo: dakika × kalori/dk (eğim ve hız bonusu)
        bonus = 1 + (incline * 0.03) + (max(0, speed - 5) * 0.02)
        calories_burned = duration * cal_per_min * bonus
    elif sets > 0 and reps > 0:
        # Ağırlık: set × tekrar × 0.5 + ağırlık bonusu
        calories_burned = sets * reps * 0.5 + (weight_kg * 0.1 * sets * reps)
    else:
        calories_burned = duration * cal_per_min if duration > 0 else 0

    entry = ExerciseLog(
        user_id=current_user.id,
        date=log_date,
        exercise_name=exercise_name,
        category=category,
        duration=duration,
        sets=sets,
        reps=reps,
        weight_kg=weight_kg,
        incline=incline,
        speed=speed,
        calories_burned=round(calories_burned),
        notes=notes
    )
    db.session.add(entry)
    db.session.commit()
    flash(f'{exercise_name} eklendi! 🏋️', 'success')
    return redirect(url_for('exercise.log', date=log_date.isoformat()))


@exercise_bp.route('/exercise/delete/<int:id>')
@login_required
def delete(id):
    entry = ExerciseLog.query.get_or_404(id)
    if entry.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('exercise.log'))

    log_date = entry.date.isoformat()
    db.session.delete(entry)
    db.session.commit()
    flash('Kayıt silindi.', 'info')
    return redirect(url_for('exercise.log', date=log_date))


@exercise_bp.route('/exercise/programs')
@login_required
def programs():
    return render_template('exercise/programs.html', programs=PROGRAMS)


@exercise_bp.route('/exercise/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    logs = ExerciseLog.query.filter_by(
        user_id=current_user.id
    ).order_by(ExerciseLog.date.desc(), ExerciseLog.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('exercise/history.html', logs=logs)
