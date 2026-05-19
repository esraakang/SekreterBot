import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, static_folder='static', template_folder='templates')
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'sekreterbot.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if test_config:
        app.config.update(test_config)
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        raise RuntimeError(
            "JWT_SECRET_KEY bulunamadı. Lütfen .env dosyasına ekleyin veya ortam değişkeni olarak tanımlayın."
        )
    app.config['JWT_SECRET_KEY'] = jwt_secret_key

    db.init_app(app)
    jwt.init_app(app)

    # Loglama Ayarları
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')  # 'logs' klasörünü oluştur
        file_handler = RotatingFileHandler('logs/sekreterbot.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SekreterBot baslatildi')

    from app import models  # noqa: F401 — modellerin db'ye kayıt olması için
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    with app.app_context():
        db.create_all()
        from app.db_upgrade import upgrade_db_schema
        upgrade_db_schema()

    return app
