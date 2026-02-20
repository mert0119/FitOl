import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fitol-gizli-anahtar-2026'
    # Render'da /tmp kullan, lokalde instance/ klasörü
    if os.environ.get('RENDER'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/app.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
