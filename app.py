import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Veritabanı
    db.init_app(app)

    # Login yöneticisi
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen giriş yapın.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Health check
    @app.route('/health')
    def health():
        return jsonify(status='ok', routes=[str(r) for r in app.url_map.iter_rules()])

    # Service Worker root'tan sunulsun
    @app.route('/sw.js')
    def sw():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js',
                                   mimetype='application/javascript')

    # Blueprint'leri kaydet
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.profile import profile_bp
    from routes.food import food_bp
    from routes.exercise import exercise_bp
    from routes.water import water_bp
    from routes.measurement import measurement_bp
    from routes.diet_plan import diet_plan_bp
    from routes.calculator import calculator_bp
    from routes.reports import reports_bp
    from routes.progress import progress_bp
    from routes.ai_suggest import ai_suggest_bp
    from routes.reminder import reminder_bp
    from routes.barcode import barcode_bp
    from routes.food_photo import food_photo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(diet_plan_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(ai_suggest_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(barcode_bp)
    app.register_blueprint(food_photo_bp)

    # Veritabanını oluştur
    with app.app_context():
        # Tüm modelleri import et
        from models.food_log import FoodLog
        from models.exercise_log import ExerciseLog
        from models.water_log import WaterLog
        from models.measurement import Measurement
        from models.diet_plan import DietPlan
        from models.progress_photo import ProgressPhoto
        from models.reminder import Reminder

        if os.environ.get('RENDER'):
            # Render'da /tmp kullan
            pass
        else:
            os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
