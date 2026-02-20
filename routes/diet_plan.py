from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.diet_plan import DietPlan

diet_plan_bp = Blueprint('diet_plan', __name__)


@diet_plan_bp.route('/diet-plan')
@login_required
def index():
    plans = DietPlan.query.filter_by(
        user_id=current_user.id
    ).order_by(DietPlan.created_at.desc()).all()

    return render_template('diet_plan.html', plans=plans)


@diet_plan_bp.route('/diet-plan/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        goal = request.form.get('goal', 'koruma')

        if not name:
            flash('Plan adı gerekli.', 'error')
            return redirect(url_for('diet_plan.create'))

        # TDEE'den kalori hesapla
        tdee = current_user.calculate_tdee()
        if tdee:
            if goal == 'kilo_verme':
                daily_calories = int(tdee - 500)
            elif goal == 'kilo_alma':
                daily_calories = int(tdee + 500)
            else:
                daily_calories = int(tdee)
        else:
            daily_calories = int(request.form.get('daily_calories', 2000))

        protein_ratio = float(request.form.get('protein_ratio', 30))
        carb_ratio = float(request.form.get('carb_ratio', 40))
        fat_ratio = float(request.form.get('fat_ratio', 30))

        plan = DietPlan(
            user_id=current_user.id,
            name=name,
            goal=goal,
            daily_calories=daily_calories,
            protein_ratio=protein_ratio,
            carb_ratio=carb_ratio,
            fat_ratio=fat_ratio,
            breakfast=request.form.get('breakfast', ''),
            lunch=request.form.get('lunch', ''),
            dinner=request.form.get('dinner', ''),
            snacks=request.form.get('snacks', ''),
            notes=request.form.get('notes', '')
        )

        # Diğer planları pasif yap
        DietPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})

        db.session.add(plan)
        db.session.commit()
        flash('Diyet planı oluşturuldu! 🥗', 'success')
        return redirect(url_for('diet_plan.index'))

    return render_template('diet_plan_create.html')


@diet_plan_bp.route('/diet-plan/delete/<int:id>')
@login_required
def delete(id):
    plan = DietPlan.query.get_or_404(id)
    if plan.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('diet_plan.index'))

    db.session.delete(plan)
    db.session.commit()
    flash('Plan silindi.', 'info')
    return redirect(url_for('diet_plan.index'))


@diet_plan_bp.route('/diet-plan/activate/<int:id>')
@login_required
def activate(id):
    plan = DietPlan.query.get_or_404(id)
    if plan.user_id != current_user.id:
        flash('Yetkisiz işlem.', 'error')
        return redirect(url_for('diet_plan.index'))

    DietPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
    plan.is_active = True
    db.session.commit()
    flash('Plan aktif edildi! ✅', 'success')
    return redirect(url_for('diet_plan.index'))
